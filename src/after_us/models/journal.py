from sqlmodel import SQLModel, Field
from datetime import datetime
from datetime import date as Date
from typing import Optional
from enum import Enum



class Journal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    description: str = Field(max_length=2000)
    date: Date
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

