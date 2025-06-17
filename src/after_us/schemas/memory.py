from pydantic import BaseModel
from datetime import datetime
from datetime import date as Date
from typing import Optional
from ..models.memory import MemoryType


class CreateMemoryRequest(BaseModel):
    title: str
    description: str
    date: Date
    type: MemoryType = MemoryType.OTHER
    mood: Optional[str] = None
    participants: list[str]
    image_url: Optional[str] = None
    extracted_from_chat: Optional[bool] = False
    chatSessionId: Optional[int] = None


class UpdateMemoryRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[Date] = None
    type: Optional[MemoryType] = None
    mood: Optional[str] = None
    participants: Optional[str] = None
    image_url: Optional[str] = None
    extracted_from_chat: Optional[bool] = False
    chat_session_id: Optional[int] = None


class MemoryResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    date: Date
    type: MemoryType
    mood: Optional[str]
    participants: str
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    extracted_from_chat: Optional[bool] = False
    chat_session_id: Optional[int] = None
