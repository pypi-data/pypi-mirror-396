from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any, Optional

class AudioProcessRequest(BaseModel):
    audio_data: bytes
    request_id: str
    user_id: str
    options: Dict[str, Any] = {} 

class AudioProcess(BaseModel):
    id: Optional[int] = None
    status: str
    audio_url: str
    created_at: datetime
    
    class Config:
        from_attributes = True 