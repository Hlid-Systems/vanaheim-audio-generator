from supabase import create_client, Client
from app.infrastructure.config.settings import settings
from app.domain.ports import SimulationRepository
from app.domain.models import SimulationRecord
from app.infrastructure.monitoring.logger import logger

class SupabaseAdapter(SimulationRepository):
    def __init__(self):
        try:
            self.url = settings.SUPABASE_URL
            self.key = settings.SUPABASE_KEY
            if not self.url or not self.key:
                logger.warning("Supabase credentials missing. DB save will fail.")
                self.client = None
            else:
                self.client: Client = create_client(self.url, self.key)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None

    async def save_simulation(self, record: SimulationRecord) -> SimulationRecord:
        if not self.client:
            logger.warning("Supabase client not initialized. Skipping save.")
            return record
            
        try:
            # Note: supabase-py v2 client is synchronous by default. 
            # In a high-perf async app, we might want to wrap this or use postgrest-py async.
            # For V1, direct call is acceptable.
            data = record.model_dump(exclude_none=True)
            
            self.client.table("vanaheim_audio").insert(data).execute()
            logger.info(f"Saved simulation record to DB: {record.id}")
            return record
        except Exception as e:
            logger.error(f"Failed to save simulation to Supabase: {e}")
            # We enforce resilience: don't crash the main response if logging fails
            return record