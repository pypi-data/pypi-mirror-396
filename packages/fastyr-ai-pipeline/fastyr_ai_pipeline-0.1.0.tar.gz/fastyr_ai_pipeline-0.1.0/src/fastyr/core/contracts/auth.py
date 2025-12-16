from pydantic import BaseModel
from typing import List

class AuthData(BaseModel):
    user_id: str
    scopes: List[str] = []