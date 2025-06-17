from sqlmodel import SQLModel, Field
from datetime import datetime
from datetime import date as Date
from typing import Optional
from enum import Enum


class MemoryType(str, Enum):
    FIRST_MEETING = "first-meeting"
    SWEET_MOMENT = "sweet-moment"
    CONFLICT = "conflict"
    MILESTONE = "milestone"
    LAST_CONTACT = "last-contact"
    OTHER = "other"


class Memory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=255)
    description: str = Field(max_length=2000)
    date: Date
    type: MemoryType = Field(default=MemoryType.OTHER)
    mood: Optional[str] = Field(
        default=None, max_length=50
    )  # e.g., "happy", "sad", "nostalgic"
    participants: str = Field(max_length=500)  # JSON string of participant names
    image_url: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    extracted_from_chat: Optional[bool] = False
    chat_session_id: Optional[int] = None

