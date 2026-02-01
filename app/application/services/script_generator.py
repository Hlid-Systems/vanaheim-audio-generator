import json
from typing import List
from app.domain.models import SimulationRequest, ScriptSegment, Script
from app.domain.ports import LLMProvider
from app.application.prompts import ScenarioPrompts
from app.infrastructure.monitoring.logger import logger

class ScriptGenerationService:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def _parse_segments(self, content: str) -> List[ScriptSegment]:
        """Parses the raw LLM response string into ScriptSegment objects."""
        try:
            # Clean content 
            content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            
            raw_segments = []
            if isinstance(data, dict):
                 if "segments" in data:
                     raw_segments = data["segments"]
                 elif "script" in data:
                     raw_segments = data["script"]
                 else:
                     for val in data.values():
                         if isinstance(val, list):
                             raw_segments = val
                             break
            elif isinstance(data, list):
                raw_segments = data
                
            if not raw_segments and isinstance(data, dict):
                 # Fallback, maybe empty
                 logger.warning(f"Could not find 'segments' list in response keys: {data.keys()}")
                 return []
    
            return [ScriptSegment(**seg) for seg in raw_segments]

        except json.JSONDecodeError:
            logger.error(f"JSON Decode Error. Raw Content: {content}")
            return []
        except Exception as e:
            logger.error(f"Error parsing segments: {e}")
            return []

    async def generate_script(self, request: SimulationRequest, api_key: str = None) -> Script:
        """
        Generates a script for the simulation using an LLM iteratively to meet duration goals.
        """
        logger.info(f"Generating script for ({request.scenario}) topic: {request.topic}")
        
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
                content = await self.llm.generate_text(messages, response_format="json", api_key=api_key, model=request.model)
                
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

        return Script(segments=all_segments)

    async def generate_script_from_prompt(self, request: "PromptRequest", api_key: str = None) -> Script:
        """
        Generates a script based on a free-form prompt/instruction.
        Enforces JSON output for audio compatibility.
        """
        logger.info(f"Generating script from prompt: {request.prompt[:50]}...")
        
        system_prompt = (
            "You are an expert scriptwriter/director. "
            "Convert the user's request into a structured audio script JSON.\n"
            "STRICT OUTPUT FORMAT:\n"
            "{\n"
            "  \"segments\": [\n"
            "    {\"role\": \"Narrator\", \"name\": \"Narrator\", \"text\": \"...\", \"voice\": \"en-US-AriaNeural\"},\n"
            "    {\"role\": \"Character\", \"name\": \"Bob\", \"text\": \"...\", \"voice\": \"en-US-GuyNeural\"}\n"
            "  ]\n"
            "}\n"
            "Choose appropriate voices (en-US-*) for the characters/roles implied."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.prompt}
        ]

        try:
            content = await self.llm.generate_text(messages, response_format="json", api_key=api_key, model=request.model)
            segments = self._parse_segments(content)
            
            if not segments:
                raise ValueError("LLM returned no valid segments for prompt.")
                
            return Script(segments=segments, metadata={"source": "prompt", "prompt": request.prompt})
            
        except Exception as e:
            logger.error(f"Prompt generation failed: {e}")
            raise