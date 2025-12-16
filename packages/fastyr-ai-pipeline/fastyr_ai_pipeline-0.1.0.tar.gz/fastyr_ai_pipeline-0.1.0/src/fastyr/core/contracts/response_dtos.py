from pydantic import BaseModel
from datetime import datetime

class AudioProcessResponse(BaseModel):
    id: int
    status: str
    created_at: datetime
    audio_url: str
    
    class Config:
        orm_mode = True 