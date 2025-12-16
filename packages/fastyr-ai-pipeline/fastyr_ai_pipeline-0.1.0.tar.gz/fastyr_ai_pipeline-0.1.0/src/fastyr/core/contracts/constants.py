from enum import Enum

class ProviderType(str, Enum):
    """Supported provider types."""
    SST = "sst"
    LLM = "llm"
    TTS = "tts"

class ErrorCodes(str, Enum):
    """Standardized error codes"""
    UNAUTHORIZED = "AUTH_001"
    INVALID_INPUT = "VAL_001"
    PROVIDER_ERROR = "PRV_001"
    RATE_LIMITED = "RAT_001"
    INTERNAL_ERROR = "INT_001"

# API Configuration

API_VERSION = "v1"
DEFAULT_TIMEOUT = 30 # seconds
MAX_RETRIES = 3