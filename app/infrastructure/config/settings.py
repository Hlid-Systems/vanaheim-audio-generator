import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Simulation Audio Generator Service"
    DATA_DIR: str = os.path.join(os.getcwd(), "data")
    SCRIPTS_DIR: str = os.path.join(os.getcwd(), "data", "scripts")
    OUTPUT_DIR: str = os.path.join(os.getcwd(), "data", "output")
    TEMP_DIR: str = os.path.join(os.getcwd(), "temp_segments")
    
    OPENAI_API_KEY: Optional[str] = None
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Directories should be created by the Application or Infrastructure setup, not on module import.