from typing import List, Dict
from openai import AsyncOpenAI
from app.domain.ports import LLMProvider
from app.infrastructure.config.settings import settings
from app.infrastructure.monitoring.logger import logger

class OpenAIAdapter(LLMProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def generate_text(self, messages: List[Dict[str, str]], response_format: str = "json", api_key: str = None, model: str = "gpt-4-turbo-preview") -> str:
        format_type = {"type": "json_object"} if response_format == "json" else None
        
        # Use provided key or fallback to default client (which has env key)
        client = self.client
        if api_key:
            # Instantiate a temp client for this request? 
            # Or pass api_key to the creation method call? 
            # The async client is usually instantiated once. 
            # Creating a new client per request might be overhead but safer for dynamic keys.
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key)
        
        if not client:
            raise ValueError("OpenAI API Key is required. Please set OPENAI_API_KEY in .env or provide X-OpenAI-Key header.")
            
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                response_format=format_type
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            raise