import edge_tts
from app.domain.ports import TTSProvider
from app.infrastructure.monitoring.logger import logger

class EdgeTTSAdapter(TTSProvider):
    async def generate_audio(self, text: str, voice: str, output_path: str) -> str:
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"EdgeTTS generation failed for voice {voice}: {e}")
            raise
