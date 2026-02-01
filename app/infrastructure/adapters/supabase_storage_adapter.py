from app.domain.ports import StorageProvider
from app.infrastructure.config.settings import settings
from app.infrastructure.monitoring.logger import logger
import os

class SupabaseStorageAdapter(StorageProvider):
    def __init__(self, bucket_name: str = "vanaheim-bucket"):
        self.bucket_name = bucket_name
        try:
            from supabase import create_client
            self.url = settings.SUPABASE_URL
            self.key = settings.SUPABASE_KEY
            if self.url and self.key:
                self.client = create_client(self.url, self.key)
            else:
                self.client = None
                logger.warning("Supabase credentials missing. Cloud Storage disabled.")
        except ImportError:
            self.client = None
            logger.error("Supabase library not installed.")

    async def save_file(self, content: bytes, path: str) -> str:
        """
        Uploads file to Supabase Storage.
        path: Relative path in bucket (e.g., 'audios/session_1.mp3')
        Returns: Public URL or Path
        """
        if not self.client:
            logger.warning("Storage client not ready. Saving to local fallback required.")
            return ""

        try:
            # Check if bucket exists, if not create? (Supabase requires API for this, or UI)
            # We assume bucket exists for V1 to be safe.
            
            # Upload (upsert=true overwrites if exists)
            res = self.client.storage.from_(self.bucket_name).upload(
                path=path,
                file=content,
                file_options={"upsert": "true"}
            )
            
            # Generate Signed URL (Valid for 1 hour)
            # Strategy: We don't save the Signed URL in DB (it expires).
            # We save the 'path' in DB, and generate the URL on demand when requested.
            # But the Port says 'save_file' returns str.
            # For V1, we return the path reference, NOT the URL.
            return path
        except Exception as e:
            logger.error(f"Failed to upload to Supabase: {e}")
            return ""

    async def concatenate_files(self, file_paths: list[str], output_path: str) -> str:
        # Complex in Cloud. For V1, we might do this locally then upload result.
        logger.warning("Cloud concatenation not implemented. Use local processing.")
        return ""

    def create_temp_dir(self, identifier: str) -> str:
        # Local op
        path = os.path.join(settings.TEMP_DIR, identifier)
        os.makedirs(path, exist_ok=True)
        return path

    def cleanup_temp_dir(self, path: str):
        # Local op
        try:
            import shutil
            shutil.rmtree(path)
        except Exception as e:
            logger.error(f"Failed to cleanup temp dir {path}: {e}")
