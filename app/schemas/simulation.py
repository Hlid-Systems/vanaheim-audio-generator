from typing import List, Optional
from pydantic import BaseModel, Field

class ScriptSegment(BaseModel):
    voice: str = Field(..., description="The EdgeTTS voice ID to use (e.g., 'es-AR-ElenaNeural').")
    role: str = Field(..., description="The role of the speaker (e.g., 'Scrum Master').")
    name: str = Field(..., description="The name of the character.")
    text: str = Field(..., description="The text to be spoken.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "voice": "es-AR-ElenaNeural",
                    "role": "Scrum Master",
                    "name": "Elena",
                    "text": "Hola equipo, bienvenidos a la Daily de hoy. ¿Quién quiere empezar?"
                }
            ]
        }
    }

class Script(BaseModel):
    segments: List[ScriptSegment]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "segments": [
                        {
                            "voice": "es-AR-ElenaNeural",
                            "role": "Scrum Master",
                            "name": "Elena",
                            "text": "Hola equipo, bienvenidos a la Daily. ¿Cómo van con el ticket de login?"
                        },
                        {
                            "voice": "es-ES-AlvaroNeural",
                            "role": "Developer",
                            "name": "Álvaro",
                            "text": "Hola Elena, ayer terminé el backend pero estoy teniendo problemas con la integración en el frontend."
                        }
                    ]
                }
            ]
        }
    }

class AudioGenerationRequest(BaseModel):
    script_name: str = Field(..., description="The name of the JSON script file in data/scripts (without .json extension).")
    output_filename: Optional[str] = Field(None, description="Optional custom output filename.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "script_name": "a1b2_p4_t5m",
                    "output_filename": "mi_audio_personalizado.mp3"
                }
            ]
        }
    }

class SimulationRequest(BaseModel):
    participants: int = Field(..., ge=2, le=10, description="Number of participants in the simulation.")
    duration_minutes: int = Field(..., ge=1, le=120, description="Approximate duration of the simulation in minutes.")
    topic: str = Field(..., description="The main topic of the meeting (e.g., 'Sprint Planning', 'Incident Review').")
    context: str = Field(..., description="Additional context (e.g., 'A fintech startup struggling with legacy code').")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "participants": 4,
                    "duration_minutes": 5,
                    "topic": "Retrospectiva del Sprint",
                    "context": "El equipo no cumplió con el objetivo del sprint debido a caídas inesperadas. El Product Owner está frustrado, pero el Líder Técnico defiende al equipo."
                }
            ]
        }
    }

class GenerationResponse(BaseModel):
    job_id: str
    status: str
    message: str
    output_file: Optional[str] = None