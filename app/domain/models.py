from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Enums ---
class AIModel(str, Enum):
    GPT_5_2_PRO = "gpt-5.2-pro"
    GPT_4_1 = "gpt-4.1"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"

class ScenarioType(str, Enum):
    CORPORATE = "CORPORATE"
    PODCAST = "PODCAST"
    STORY = "STORY"

class VoiceEnum(str, Enum):
    # English (US)
    EN_US_ARIA = "en-US-AriaNeural"
    EN_US_GUY = "en-US-GuyNeural"
    EN_US_JENNY = "en-US-JennyNeural"
    
    # Spanish (Mexico/Spain/Latam)
    ES_MX_DALIA = "es-MX-DaliaNeural"
    ES_MX_JORGE = "es-MX-JorgeNeural"
    ES_ES_ELVIRA = "es-ES-ElviraNeural"
    ES_ES_ALVARO = "es-ES-AlvaroNeural"
    ES_AR_ELENA = "es-AR-ElenaNeural"
    ES_VE_SEBASTIAN = "es-VE-SebastianNeural"
    ES_CO_GONZALO = "es-CO-GonzaloNeural"
    ES_US_PALOMA = "es-US-PalomaNeural"

    # French
    FR_FR_DENISE = "fr-FR-DeniseNeural"
    FR_FR_HENRI = "fr-FR-HenriNeural"

    # German
    DE_DE_KATJA = "de-DE-KatjaNeural"
    DE_DE_CONRAD = "de-DE-ConradNeural"

    # Italian
    IT_IT_ELSA = "it-IT-ElsaNeural"
    IT_IT_ISABELLA = "it-IT-IsabellaNeural"

# --- Entities ---
class ScriptSegment(BaseModel):
    voice: str = Field(..., description="The TTS voice ID.")
    role: str = Field(..., description="Speaker role.")
    name: str = Field(..., description="Speaker name.")
    text: str = Field(..., description="Text content.")

class Script(BaseModel):
    segments: List[ScriptSegment]
    metadata: Optional[dict] = Field(default_factory=dict)

class SimulationRequest(BaseModel):
    """Specialized Scenario Mode (e.g. Corporate, Podcast) with Timer"""
    participants: int = Field(..., ge=2, le=10)
    duration_minutes: int = Field(..., ge=1, le=120, description="Target duration in minutes (1-120).")
    topic: str
    context: str
    scenario: ScenarioType = Field(default=ScenarioType.CORPORATE)
    model: AIModel = Field(default=AIModel.GPT_4_TURBO, description="OpenAI Model to use.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "participants": 3,
                    "duration_minutes": 3,
                    "topic": "Sprint Planning Failure",
                    "context": "The backend team is explaining why the migration failed.",
                    "scenario": "CORPORATE",
                    "model": "gpt-4-turbo"
                }
            ]
        }
    }

class TextRequest(BaseModel):
    """Free Mode: Simple Text to Audio"""
    text: str = Field(..., description="The text to convert to audio.")
    voice: VoiceEnum = Field(default=VoiceEnum.EN_US_ARIA, description="Select a high-quality neural voice.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Welcome to Hlid Systems. All systems operating at peak efficiency.",
                    "voice": "en-US-AriaNeural"
                }
            ]
        }
    }

class PromptRequest(BaseModel):
    """Dev Mode: Open Prompt to Audio"""
    prompt: str = Field(..., description="The instruction/prompt for the LLM (e.g. 'Create a dialog between 2 pirates').")
    topic: Optional[str] = "General"
    context: Optional[str] = None
    model: AIModel = Field(default=AIModel.GPT_4_TURBO, description="OpenAI Model to use.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "Genera una discusión tensa entre un arquitecto de software y un manager sobre deuda técnica.",
                    "topic": "Deuda Técnica",
                    "context": "Revisión trimestral",
                    "model": "gpt-4-turbo"
                }
            ]
        }
    }

class AudioRequest(BaseModel):
    """Request for Direct Text-to-Audio (No LLM generation)"""
    script: Script
    output_filename: Optional[str] = None

class SimulationRecord(BaseModel):
    """Corresponds to vanaheim_audio table"""
    id: Optional[str] = None
    created_at: Optional[str] = None
    topic: str
    context: str
    duration_minutes: int
    participants_count: int
    script_path: str
    audio_path: str
    configuration: Optional[dict] = Field(default_factory=dict, description="Stores model, voices used, etc.")
    script_content: Optional[str] = Field(None, description="The actual generated script text.")