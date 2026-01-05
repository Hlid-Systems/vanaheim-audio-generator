import json
import re
import os
import uuid
import time
from typing import List
from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.simulation import SimulationRequest, ScriptSegment
from app.core.logging import logger

class ScriptService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def analyze_script(self, segments: List[ScriptSegment]) -> tuple[int, int]:
        """
        Analyzes the script to estimate metadata for naming.
        Returns: (participant_count, duration_minutes)
        """
        # Count unique names/roles combination to determine participants
        unique_participants = set((s.role, s.name) for s in segments)
        count = len(unique_participants)
        
        # Estimate duration: ~150 words per minute
        total_words = sum(len(s.text.split()) for s in segments)
        duration = max(1, round(total_words / 150))
        
        return count, duration

    async def generate_script(self, request: SimulationRequest) -> List[ScriptSegment]:
        """
        Generates a script for the simulation using an LLM.
        """
        logger.info(f"Generating script for topic: {request.topic} with {request.participants} participants.")
        
        system_prompt = """
        Eres un experto guionista para simulaciones de ingeniería de software ágil.
        Tu tarea es generar un guion JSON para una API de simulación de voz.
        
        La salida debe ser estrictamente un OBJETO JSON con una clave "segments" que contenga la lista de turnos.
        Estructura:
        {
          "segments": [
            {
                "voice": "string (ID de voz de EdgeTTS)",
                "role": "string (Cargo/Rol)",
                "name": "string (Nombre de pila)",
                "text": "string (Diálogo en Español)"
            }
          ]
        }

        Voces Disponibles (Asigna apropiadamente para variedad de género/rol):
        - es-AR-ElenaNeural (Mujer)
        - es-ES-AlvaroNeural (Hombre)
        - es-VE-SebastianNeural (Hombre)
        - es-MX-DaliaNeural (Mujer)
        - es-CO-GonzaloNeural (Hombre)
        - es-US-PalomaNeural (Mujer)

        REGLAS CRÍTICAS:
        1. Contexto: Los participantes son un equipo de desarrollo de software.
        2. Introducción: En el PRIMER turno de habla de CADA personaje, DEBEN presentarse usando el formato: "... Soy [Nombre] [Apellido]...". Todas las presentaciones deben ocurrir dentro de los primeros 3 o 4 turnos de la conversación (aprox. los primeros 30 segundos).
        3. Realismo: El diálogo debe ser técnico, profesional pero realista para un equipo ágil (Daily, Planning, Retro, o Incidente).
        4. Idioma: Español.
        5. Formato de Salida: JSON Puro.
        """

        user_prompt = f"""
        Genera un guion con los siguientes parámetros:
        - Participantes: {request.participants}
        - Tema: {request.topic}
        - Contexto: {request.context}
        - Duración Aproximada: {request.duration_minutes} minutos (Asume ~150 palabras por minuto).
        
        Asegúrate de que la conversación fluya naturalmente y resuelva un problema o aborde el tema propuesto.
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
    
            content = response.choices[0].message.content
            
            # Clean content (strip markdown fences if any)
            content = content.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(content)
            
            # Extract segments
            if isinstance(data, dict):
                 if "segments" in data:
                     raw_segments = data["segments"]
                 elif "script" in data:
                     raw_segments = data["script"]
                 else:
                     # Attempt to find any list in values
                     found_list = None
                     for val in data.values():
                         if isinstance(val, list):
                             found_list = val
                             break
                     if found_list:
                         raw_segments = found_list
                     else:
                        raise ValueError(f"Could not find 'segments' list in response keys: {data.keys()}")
            elif isinstance(data, list):
                raw_segments = data
            else:
                raise ValueError("Response is not a list or a dict containing a list.")
    
            # Validate against our Pydantic model
            segments = [ScriptSegment(**seg) for seg in raw_segments]
            return segments

        except json.JSONDecodeError:
            logger.error(f"JSON Decode Error. Raw Content: {content}")
            raise ValueError("LLM did not return valid JSON.")
        except Exception as e:
            logger.error(f"Error during script generation: {e}")
            raise ValueError(f"Failed to generate script: {str(e)}")