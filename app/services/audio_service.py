import os
import shutil
import edge_tts
from typing import List
from app.core.config import settings
from app.schemas.simulation import ScriptSegment
from app.core.logging import logger

class AudioService:
    @staticmethod
    async def generate_segment_audio(segment: ScriptSegment, index: int, output_dir: str) -> str:
        """Generates audio for a single segment."""
        filename = f"segment_{index:03d}.mp3"
        filepath = os.path.join(output_dir, filename)
        
        try:
            communicate = edge_tts.Communicate(segment.text, segment.voice)
            await communicate.save(filepath)
            return filepath
        except Exception as e:
            logger.error(f"Error generating segment {index} ({segment.role}): {e}")
            raise

    @staticmethod
    async def concatenate_audio_files(segment_files: List[str], output_file: str):
        """Concatenates multiple MP3 files into one."""
        logger.info(f"Concatenating {len(segment_files)} segments into {output_file}")
        with open(output_file, 'wb') as outfile:
            for file_path in segment_files:
                with open(file_path, 'rb') as infile:
                    shutil.copyfileobj(infile, outfile)

    async def process_script(self, segments: List[ScriptSegment], output_filename: str) -> str:
        """Main pipeline to process a list of segments and produce a final audio file."""
        temp_dir = os.path.join(settings.TEMP_DIR, output_filename.replace(".mp3", ""))
        final_output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
        
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        logger.info(f"Starting audio generation for {len(segments)} segments.")
        
        generated_files = []
        try:
            for i, segment in enumerate(segments):
                logger.debug(f"Processing segment {i+1}/{len(segments)}: {segment.role}")
                audio_file = await self.generate_segment_audio(segment, i, temp_dir)
                generated_files.append(audio_file)

            await self.concatenate_audio_files(generated_files, final_output_path)
            logger.info(f"Audio saved successfully to: {final_output_path}")

        except Exception as e:
            logger.error(f"Process failed: {e}")
            raise
        finally:
            # Cleanup temp files
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Could not clean up temp directory {temp_dir}: {e}")

        return final_output_path