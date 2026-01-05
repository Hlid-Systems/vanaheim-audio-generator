from typing import List, Optional
from pydantic import BaseModel, Field

from enum import Enum

class ScenarioType(str, Enum):
    CORPORATE = "CORPORATE"
    PODCAST = "PODCAST"
    STORY = "STORY"
    # EDUCATION = "EDUCATION" # Future expansion

class ScriptSegment(BaseModel):
    voice: str = Field(..., description="The EdgeTTS voice ID to use (e.g., 'es-AR-ElenaNeural').")
    role: str = Field(..., description="The role of the speaker (e.g., 'Team Lead').")
    name: str = Field(..., description="The name of the character.")
    text: str = Field(..., description="The text to be spoken.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "voice": "es-AR-ElenaNeural",
                    "role": "Team Lead",
                    "name": "Elena",
                    "text": "Hola equipo, bienvenidos a la reunión de hoy. ¿Quién quiere empezar?"
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
                            "role": "Team Lead",
                            "name": "Elena",
                            "text": "Hola equipo, bienvenidos a la reunión. ¿Cómo van con el módulo de login?"
                        },
                        {
                            "voice": "es-ES-AlvaroNeural",
                            "role": "Engineer",
                            "name": "Álvaro",
                            "text": "Hola Elena, ayer terminé el backend pero estoy revisando la integración."
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
    topic: str = Field(..., description="The main topic of the meeting (e.g., 'Project Review', 'Architecture Discussion').")
    context: str = Field(..., description="Additional context (e.g., 'A fintech startup discussing new features').")
    scenario: ScenarioType = Field(default=ScenarioType.CORPORATE, description="The type of simulation to generate.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "participants": 4,
                    "duration_minutes": 5,
                    "topic": "Revisión de Proyecto",
                    "context": "El equipo analiza los retrasos en la entrega del módulo Q3 debido a problemas de integración.",
                    "scenario": "CORPORATE"
                },
                 {
                    "participants": 2,
                    "duration_minutes": 3,
                    "topic": "Entrevista sobre IA",
                    "context": "Un host entrevista a un experto sobre el impacto de la IA en el arte.",
                    "scenario": "PODCAST"
                }
            ]
        }
    }

class GenerationResponse(BaseModel):
    job_id: str
    status: str
    message: str
    output_file: Optional[str] = None