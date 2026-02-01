import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from fastapi.responses import FileResponse
import json
from typing import Optional

from app.domain.models import SimulationRequest, Script, TextRequest, PromptRequest, ScriptSegment, VoiceEnum
from app.infrastructure.api.schemas import GenerationResponse

# Application Services
from app.application.services.script_generator import ScriptGenerationService
from app.application.services.audio_generator import AudioGenerationService

# Adapters (Dependency Injection root could be here or main)
from app.infrastructure.adapters.openai_adapter import OpenAIAdapter
from app.infrastructure.adapters.edge_tts_adapter import EdgeTTSAdapter
from app.infrastructure.adapters.file_storage_adapter import FileStorageAdapter
from app.infrastructure.adapters.supabase_adapter import SupabaseAdapter
from app.infrastructure.adapters.supabase_storage_adapter import SupabaseStorageAdapter
from app.infrastructure.monitoring.logger import logger
from app.domain.models import SimulationRecord
from datetime import datetime, timezone

router = APIRouter()

# Instantiate Adapters
llm_provider = OpenAIAdapter()
tts_provider = EdgeTTSAdapter()
# Let's keep it simple: Application Service takes 'local_storage' and optional 'cloud_storage'.
storage_provider = FileStorageAdapter() 
cloud_storage = SupabaseStorageAdapter() # New instance
db_repository = SupabaseAdapter()

# Instantiate Services
script_service = ScriptGenerationService(llm_provider)
audio_service = AudioGenerationService(tts_provider, storage_provider, cloud_storage)

@router.post("/tts/simple", tags=["TTS"])
async def generate_simple_tts(request: TextRequest):
    """
    **Free Mode: Simple Text-to-Audio**
    
    Converts plain text to audio using a specific voice without using LLMs.
    
    - **No API Key required**.
    - **Fast generation**.
    """
    job_id = str(uuid.uuid4())
    try:
        # Create a single-segment script
        script = Script(segments=[
            ScriptSegment(
                role="Narrator",
                name="Narrator",
                text=request.text,
                voice=request.voice
            )
        ])
        
        output_filename = f"{job_id}_simple.mp3"
        final_path = await audio_service.generate_script_audio(script, output_filename, upload_to_cloud=False)
        
        # Return File Directly for Download
        return FileResponse(
            path=final_path,
            filename=f"simple_tts_{job_id}.mp3",
            media_type="audio/mpeg"
        )
    except Exception as e:
        logger.error(f"Simple TTS failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/prompt", tags=["AI Tools"])
async def generate_from_prompt(
    request: PromptRequest,
    x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key")
):
    """
    **Dev Mode: Prompt -> AI Script -> Audio**
    
    Generates a full audio script from a natural language prompt.
    
    - **Requires X-OpenAI-Key header**.
    - **Persists data** to Supabase (if configured).
    """
    # If header is missing, check if we have a default env key (handled by Adapter), 
    # but we should explicit check here to fail fast if neither exists
    from app.infrastructure.config.settings import settings
    if not x_openai_key and not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=401, detail="X-OpenAI-Key header required (no server-side key configured).")

    job_id = str(uuid.uuid4())
    try:
        # 1. Generate Script from Prompt
        script = await script_service.generate_script_from_prompt(request, api_key=x_openai_key)
        
        # 2. Save Script JSON (Reuse logic or abstract? Copy-paste for V1 speed/safety)
        script_filename = f"{job_id}_prompt.json"
        
        # Lazy import to avoid circular dep issues if any
        from app.infrastructure.config.settings import settings
        import os
        script_path = os.path.join(settings.SCRIPTS_DIR, script_filename)
        
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(script.model_dump(), f, indent=4, ensure_ascii=False)

        # 3. Generate Audio
        output_filename = f"{job_id}_prompt.mp3"
        final_path = await audio_service.generate_script_audio(script, output_filename)
        
        # 4. Save to DB
        try:
            record = SimulationRecord(
                id=job_id,
                created_at=datetime.now(timezone.utc).isoformat(),
                topic=request.topic or "Prompt Generation",
                context=request.prompt, # Context is the prompt
                duration_minutes=0, # Unknown/Variable
                participants_count=len(script.segments), # Count roles? or segments
                script_path=script_path,
                audio_path=final_path,
                configuration={"model": request.model.value, "prompt": request.prompt},
                script_content=json.dumps(script.model_dump(), ensure_ascii=False)
            )
            await db_repository.save_simulation(record)
        except Exception as db_e:
            logger.error(f"DB Recording error: {db_e}")

        # Return File Directly (User Requirement: Immediate Audio Playback/Download)
        return FileResponse(
            path=final_path,
            filename=f"prompt_{job_id}.mp3",
            media_type="audio/mpeg",
            headers={
                "X-Vanaheim-Job-Id": job_id,
                "X-Vanaheim-Script-Preview": request.prompt[:100].replace("\n", " ")  # Brief preview in header
            }
        )
    except Exception as e:
        logger.error(f"Dev Mode failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulation/scenario", tags=["Simulations"])
async def generate_from_scenario(
    request: SimulationRequest, 
    x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key")
):
    """
    **Specialized Mode: Complex Scenario Simulation**
    
    Generates a multi-role dialogue based on specific constraints:
    - Participants count
    - Duration limit (minutes)
    - Specific topic and context
    
    - **Requires X-OpenAI-Key header** (or server env).
    """
    job_id = str(uuid.uuid4())
    try:
        # 1. Generate Script
        script = await script_service.generate_script(request, api_key=x_openai_key)
        
        # 2. Save Script
        script_filename = f"{job_id}_{request.scenario}.json"
        from app.infrastructure.config.settings import settings
        import os
        script_path = os.path.join(settings.SCRIPTS_DIR, script_filename)
        
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(script.model_dump(), f, indent=4, ensure_ascii=False)

        # 3. Generate Audio
        output_filename = f"{job_id}_{request.scenario}.mp3"
        final_path = await audio_service.generate_script_audio(script, output_filename)
        
        # 4. Save to DB
        try:
            record = SimulationRecord(
                id=job_id,
                created_at=datetime.now(timezone.utc).isoformat(),
                topic=request.topic,
                context=request.context,
                duration_minutes=request.duration_minutes,
                participants_count=request.participants,
                script_path=script_path,
                audio_path=final_path,
                configuration={"model": request.model.value, "scenario": request.scenario},
                script_content=json.dumps(script.model_dump(), ensure_ascii=False)
            )
            await db_repository.save_simulation(record)
        except Exception as db_e:
            logger.error(f"DB Recording error (non-fatal): {db_e}")

        # Return File Directly (User Requirement: Immediate Audio Playback/Download)
        return FileResponse(
            path=final_path,
            filename=f"scenario_{job_id}.mp3",
            media_type="audio/mpeg",
            headers={
                "X-Vanaheim-Job-Id": job_id,
                "X-Vanaheim-Participants": str(len(script.segments))
            }
        )

    except Exception as e:
        logger.error(f"Generate Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", tags=["Status"])
async def health_check():
    """
    **Health Check**
    
    Returns the operational status of the service.
    """
    return {"status": "operational", "service": "Vanaheim", "version": "1.0.0"}