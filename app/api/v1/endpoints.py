import json
import os
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.simulation import (
    SimulationRequest, 
    GenerationResponse, 
    GenerationResponse, 
    AudioGenerationRequest,
    Script,
    ScriptSegment
)
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from typing import List
from app.core.config import settings
from app.services.script_service import ScriptService
from app.services.audio_service import AudioService
from app.core.logging import logger

router = APIRouter()
script_service = ScriptService()
audio_service = AudioService()

@router.post("/simulation/generate", response_model=GenerationResponse)
async def generate_simulation(
    request: SimulationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generates a full audio simulation based on high-level parameters.
    1. Generates a script using LLM.
    2. Generates audio from the script.
    """
    # Short ID (first 4 chars of UUID)
    short_id = str(uuid.uuid4())[:4]
    
    try:
        # 1. Generate Script
        segments = await script_service.generate_script(request)
        
        # New Naming: {abcd}_p{N}_t{N}m
        # e.g., a1b2_p4_t5m
        base_filename = f"{short_id}_p{request.participants}_t{request.duration_minutes}m"
        
        script_filename = f"{base_filename}.json"
        script_path = os.path.join(settings.SCRIPTS_DIR, script_filename)
        
        with open(script_path, "w", encoding="utf-8") as f:
            # Dump Pydantic models to JSON
            json.dump([seg.model_dump() for seg in segments], f, indent=4, ensure_ascii=False)
        
        output_filename = f"{base_filename}.mp3"
        final_path = await audio_service.process_script(segments, output_filename)
        
        return GenerationResponse(
            job_id=short_id,
            status="success",
            message=f"Simulation completed. generated: {len(segments)} segments.",
            output_file=final_path
        )

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Process failed at stage: {str(e)}"
        )

@router.post("/simulation/audio-only", response_model=GenerationResponse)
async def generate_audio_only(request: AudioGenerationRequest):
    """
    Generates audio from an EXISTING script file in data/scripts.
    """
    # Short ID
    job_id = str(uuid.uuid4())[:4]
    script_path = os.path.join(settings.SCRIPTS_DIR, f"{request.script_name}.json")
    
    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail=f"Script {request.script_name}.json not found.")
        
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Map Dict to Pydantic models
            # Data validation using Pydantic
            from app.schemas.simulation import ScriptSegment
            
            if isinstance(data, list):
                segments = [ScriptSegment(**item) for item in data]
            elif isinstance(data, dict) and "segments" in data:
                 # Handle cases where json is wrapped in a dict
                segments = [ScriptSegment(**item) for item in data["segments"]]
            else:
                # Fallback or strict error
                raise ValueError("Script file format invalid (expected list or dict with 'segments').")

        output_filename = request.output_filename or f"{job_id}_audio-only.mp3"
        final_path = await audio_service.process_script(segments, output_filename)
        
        return GenerationResponse(
            job_id=job_id,
            status="completed",
            message="Audio generated successfully.",
            output_file=final_path
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _process_and_respond(segments: List[ScriptSegment]) -> GenerationResponse:
    """Helper to process segments, save files with generic convention, and return response."""
    # 1. Analyze for metadata
    participants, duration = script_service.analyze_script(segments)
    
    # 2. Generate ID and Name
    short_id = str(uuid.uuid4())[:4]
    base_filename = f"{short_id}_p{participants}_t{duration}m"
    
async def _process_and_respond(segments: List[ScriptSegment], save_script: bool = True) -> GenerationResponse:
    """Helper to process segments, optionally save script, and return response."""
    # 1. Analyze for metadata
    participants, duration = script_service.analyze_script(segments)
    
    # 2. Generate ID and Name
    short_id = str(uuid.uuid4())[:4]
    base_filename = f"{short_id}_p{participants}_t{duration}m"
    
    # 3. Save Script (Only if requested)
    if save_script:
        script_filename = f"{base_filename}.json"
        script_path = os.path.join(settings.SCRIPTS_DIR, script_filename)
            
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump([seg.model_dump() for seg in segments], f, indent=4, ensure_ascii=False)
        
    # 4. Generate Audio
    output_filename = f"{base_filename}.mp3"
    final_path = await audio_service.process_script(segments, output_filename)
    
    return GenerationResponse(
        job_id=short_id,
        status="success",
        message=f"Audio generated successfully.",
        output_file=final_path
    )

@router.post("/simulation/audio-from-file", response_model=GenerationResponse)
async def generate_audio_from_file(file: UploadFile = File(...)):
    """
    Upload a JSON script file directly.
    """
    try:
        content = await file.read()
        data = json.loads(content)
        
        # Validate / Parse
        if isinstance(data, list):
            segments = [ScriptSegment(**item) for item in data]
        elif isinstance(data, dict) and "segments" in data:
            segments = [ScriptSegment(**item) for item in data["segments"]]
        else:
             raise ValueError("Invalid JSON format. Expected list of segments or object with 'segments' key.")
             
        return await _process_and_respond(segments, save_script=False)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file.")
    except Exception as e:
        logger.error(f"File upload processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulation/audio-from-json", response_model=GenerationResponse)
async def generate_audio_from_json(script: Script):
    """
    Paste the raw JSON script in the request body.
    """
    try:
        return await _process_and_respond(script.segments, save_script=False)
    except Exception as e:
        logger.error(f"Manual script processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))