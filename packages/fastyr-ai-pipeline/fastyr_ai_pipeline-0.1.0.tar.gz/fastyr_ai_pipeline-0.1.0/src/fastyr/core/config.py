from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    DEEPGRAM_API_KEY: str
    OPENAI_API_KEY: str
    ELEVENLABS_API_KEY: str
    
    # Provider Settings
    OPENAI_MODEL: str = "gpt-4"
    ELEVENLABS_VOICE_ID: str = "default"
    
    # API URLs
    DEEPGRAM_API_URL: str = "https://api.deepgram.com/v1"
    OPENAI_API_URL: str = "https://api.openai.com/v1"
    ELEVENLABS_API_URL: str = "https://api.elevenlabs.io/v1"
    
    # Timeouts and Retries
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    
    class Config:
        env_file = ".env" 