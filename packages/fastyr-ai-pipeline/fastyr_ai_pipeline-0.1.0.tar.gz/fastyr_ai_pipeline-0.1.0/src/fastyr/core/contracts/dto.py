from dataclasses import dataclass
from typing import TypeVar, Generic
from datetime import datetime

T = TypeVar('T')

@dataclass
class BaseDto:
    """Base class for all DTOs providing common fields and validation."""

    created_at: datetime
    updated_at: datetime

@dataclass
class RequestDto(BaseDto):
    """Base class for request DTOs with common request-specific fields."""

    request_id: str
    user_id: str

@dataclass
class ResponseDto(BaseDto):
    """Base class for response DTOs with common response-specific fields."""

    status: str
    message: str

