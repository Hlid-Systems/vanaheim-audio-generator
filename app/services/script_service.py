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

from app.core.prompts import ScenarioPrompts

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
        
        # Estimate duration: 150 words per minute
        total_words = sum(len(s.text.split()) for s in segments)
        duration = max(1, round(total_words / 150))
        
        return count, duration

    def _parse_segments(self, content: str) -> List[ScriptSegment]:
        """Parses the raw LLM response string into ScriptSegment objects."""
        try:
            # Clean content 
            content = content.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(content)
            
            # Extract segments
            raw_segments = []
            if isinstance(data, dict):
                 if "segments" in data:
                     raw_segments = data["segments"]
                 elif "script" in data:
                     raw_segments = data["script"]
                 else:
                     # Attempt to find any list in values
                     for val in data.values():
                         if isinstance(val, list):
                             raw_segments = val
                             break
            elif isinstance(data, list):
                raw_segments = data
                
            if not raw_segments and isinstance(data, dict):
                 raise ValueError(f"Could not find 'segments' list in response keys: {data.keys()}")
    
            # Validate against our Pydantic model
            return [ScriptSegment(**seg) for seg in raw_segments]

        except json.JSONDecodeError:
            logger.error(f"JSON Decode Error. Raw Content: {content}")
            return []
        except Exception as e:
            logger.error(f"Error parsing segments: {e}")
            return []

    async def generate_script(self, request: SimulationRequest) -> List[ScriptSegment]:
        """
        Generates a script for the simulation using an LLM iteratively to meet duration goals.
        """
        logger.info(f"Generating script for ({request.scenario}) topic: {request.topic} with {request.participants} participants.")
        
        # Calculate target based on 150 words per minute
        target_word_count = request.duration_minutes * 150
        current_word_count = 0
        all_segments = []
        
        # Get Prompt Strategy
        system_prompt, user_prompt_template = ScenarioPrompts.get_prompt(request.scenario)

        # Initial User Prompt
        user_prompt = user_prompt_template.format(
            participants=request.participants,
            topic=request.topic,
            context=request.context,
            duration_minutes=request.duration_minutes
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        iteration = 0
        MAX_ITERATIONS = max(2, request.duration_minutes // 2 + 2)

        while current_word_count < target_word_count and iteration < MAX_ITERATIONS:
            iteration += 1
            logger.info(f"Generation Iteration {iteration}. Progress: {current_word_count}/{target_word_count} words.")
            
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=messages,
                    response_format={"type": "json_object"}
                )
        
                content = response.choices[0].message.content
                if not content:
                    logger.warning("Empty content from LLM.")
                    break

                new_segments = self._parse_segments(content)
                
                if not new_segments:
                    logger.warning("No valid segments found in current iteration.")
                    break 

                all_segments.extend(new_segments)
                
                # Update counts
                batch_words = sum(len(s.text.split()) for s in new_segments)
                current_word_count += batch_words
                
                # Prepare for next iteration if needed
                if current_word_count < target_word_count:
                    messages.append({"role": "assistant", "content": content})
                    
                    # Calculate remaining needs
                    remaining_words = target_word_count - current_word_count
                    remaining_minutes = max(1, round(remaining_words / 150))
                    
                    continuation_msg = (
                        f"¡Excelente! Pero aún necesitamos más contenido para cumplir con el tiempo objetivo.\n"
                        f"Faltan aproximadamente {remaining_words} palabras ({remaining_minutes} minutos).\n"
                        f"Continúa la simulación exactamente donde quedó. Introduce un nuevo punto de discusión, "
                        f"profundiza en un detalle técnico o genera un conflicto/resolución.\n"
                        f"MANTÉN EL FORMATO JSON. NO repitas introducciones."
                    )
                    messages.append({"role": "user", "content": continuation_msg})
                
            except Exception as e:
                logger.error(f"Error during script generation iteration {iteration}: {e}")
                break

        if not all_segments:
            raise ValueError("Failed to generate any valid script segments.")

        return all_segments