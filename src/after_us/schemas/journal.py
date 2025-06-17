from pydantic import BaseModel
from datetime import datetime
from datetime import date as Date
from typing import Optional
from ..models.memory import MemoryType


class CreateJournalRequest(BaseModel):
    description: str
    date: Date
    user_id: int


class UpdateJournalRequest(BaseModel):
    description: Optional[str] = None
    date: Optional[Date] = None
    user_id: int


class JournalResponse(BaseModel):
    id: int
    description: Optional[str] = None
    date: Optional[Date] = None
    user_id: int
