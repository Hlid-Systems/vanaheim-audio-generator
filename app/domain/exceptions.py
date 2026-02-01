class VanaheimError(Exception):
    """Base exception for all domain-level errors in Vanaheim."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ResourceNotFoundError(VanaheimError):
    """Raised when a requested resource (like a script file) is not found."""
    pass

class ConfigurationError(VanaheimError):
    """Raised when critical configuration (like API Keys) is missing."""
    pass

class GenerationError(VanaheimError):
    """Raised when the generation process (LLM or TTS) fails."""
    pass