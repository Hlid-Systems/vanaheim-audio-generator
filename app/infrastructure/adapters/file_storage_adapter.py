import os
import shutil
from typing import List
from app.domain.ports import StorageProvider
from app.infrastructure.monitoring.logger import logger
from app.infrastructure.config.settings import settings

class FileStorageAdapter(StorageProvider):
    async def save_file(self, content: bytes, path: str) -> str:
        with open(path, 'wb') as f:
            f.write(content)
        return path

    async def concatenate_files(self, file_paths: List[str], output_path: str) -> str:
        logger.info(f"Concatenating {len(file_paths)} files into {output_path}")
        with open(output_path, 'wb') as outfile:
            for file_path in file_paths:
                with open(file_path, 'rb') as infile:
                    shutil.copyfileobj(infile, outfile)
        return output_path

    def create_temp_dir(self, identifier: str) -> str:
        # Use settings for consistent pathing
        base_temp = settings.TEMP_DIR
        path = os.path.join(base_temp, identifier)
        os.makedirs(path, exist_ok=True)
        return path

    def cleanup_temp_dir(self, path: str):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                logger.debug(f"Cleaned up {path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {path}: {e}")