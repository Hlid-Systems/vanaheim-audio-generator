import os
from typing import List
from app.domain.models import Script, ScriptSegment
from app.domain.ports import TTSProvider, StorageProvider
from app.infrastructure.monitoring.logger import logger
from app.infrastructure.config.settings import settings

from typing import Optional

class AudioGenerationService:
    def __init__(self, tts_provider: TTSProvider, storage_provider: StorageProvider, cloud_storage: Optional[StorageProvider] = None):
        self.tts = tts_provider
        self.storage = storage_provider
        self.cloud_storage = cloud_storage

    async def generate_script_audio(self, script: Script, output_filename: str, upload_to_cloud: bool = True) -> str:
        """
        Orchestrates the generation of audio for a full script.
        Returns: Path to the generated file (Local or Cloud signed URL).
        """
        # Create temp dir
        safe_name = output_filename.replace(".mp3", "")
        temp_dir = self.storage.create_temp_dir(safe_name)
        # Local final destination (always required for concatenation)
        local_output_path = os.path.join(settings.OUTPUT_DIR, output_filename)

        generated_files = []
        try:
            for i, segment in enumerate(script.segments):
                filename = f"segment_{i:03d}.mp3"
                filepath = os.path.join(temp_dir, filename)
                
                logger.debug(f"Generating segment {i}: {segment.role}")
                path = await self.tts.generate_audio(segment.text, segment.voice, filepath)
                generated_files.append(path)

            # Concatenate
            if generated_files:
                await self.storage.concatenate_files(generated_files, local_output_path)
                logger.info(f"Final audio assembled locally: {local_output_path}")

                # --- Cloud Persistence (Resilient) ---
                if self.cloud_storage and upload_to_cloud:
                    try:
                        with open(local_output_path, "rb") as f:
                            file_content = f.read()
                            
                        # Upload to Cloud
                        cloud_path = await self.cloud_storage.save_file(file_content, output_filename)
                        
                        if cloud_path:
                            logger.info(f"Cloud Backup Successful: {cloud_path}")
                                 
                    except Exception as e:
                        logger.warning(f"⚠️ CLOUD UPLOAD FAILED (Quota?): {e}. Returning local file.")
                        # Do not raise! Fallback to local.
                
                return local_output_path
            else:
                raise ValueError("No audio segments generated.")

        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            raise
        finally:
            self.storage.cleanup_temp_dir(temp_dir)