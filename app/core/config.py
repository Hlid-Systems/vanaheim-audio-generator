import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Voice Analysis Simulation Service"
    DATA_DIR: str = os.path.join(os.getcwd(), "data")
    SCRIPTS_DIR: str = os.path.join(os.getcwd(), "data", "scripts")
    OUTPUT_DIR: str = os.path.join(os.getcwd(), "data", "output")
    TEMP_DIR: str = os.path.join(os.getcwd(), "temp_segments")
    
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Ensure directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.SCRIPTS_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)