from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.domain.models import ScriptSegment, SimulationRecord

class TTSProvider(ABC):
    """Port for Text-to-Speech services."""
    @abstractmethod
    async def generate_audio(self, text: str, voice: str, output_path: str) -> str:
        """Generates audio file for a given text and voice."""
        pass

class LLMProvider(ABC):
    """Port for Large Language Model services."""
    @abstractmethod
    async def generate_text(self, messages: List[Dict[str, str]], response_format: str = "json", api_key: str = None) -> str:
        """Generates text from an LLM provider."""
        pass

class StorageProvider(ABC):
    """Port for File Storage operations."""
    @abstractmethod
    async def save_file(self, content: bytes, path: str) -> str:
        pass

    @abstractmethod
    async def concatenate_files(self, file_paths: List[str], output_path: str) -> str:
        pass

    @abstractmethod
    def create_temp_dir(self, identifier: str) -> str:
        pass
    
    @abstractmethod
    def cleanup_temp_dir(self, path: str):
        pass

class SimulationRepository(ABC):
    """Port for Database Interaction"""
    @abstractmethod
    async def save_simulation(self, record: SimulationRecord) -> SimulationRecord:
        # returns the saved record or ID
        pass