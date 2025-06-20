from sqlmodel import SQLModel, Field
from datetime import datetime
from datetime import date as Date
from typing import Optional
from enum import Enum
from ..utils.Toneenum import ToneEnum


class ActivityCategory(str, Enum):
    SELF_CARE = "self-care"
    SOCIAL = "social"
    CREATIVE = "creative"
    PHYSICAL = "physical"
    EMOTIONAL = "emotional"
    PROFESSIONAL = "professional"


class NoContactDay(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    date: Date = Field(index=True)
    success: bool = Field(default=True)  # True if successfully maintained no contact
    mood: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ClosureActivity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=255)
    description: str = Field(max_length=1000)
    completed: bool = Field(default=False)
    completed_date: Optional[datetime] = Field(default=None)
    category: ActivityCategory = Field(default=ActivityCategory.EMOTIONAL)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AIPersonality(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, unique=True)
    tone: ToneEnum = Field(
        max_length=50, default=ToneEnum.SUPPORTIVE
    )  # supportive, empathetic, challenging, etc.
    mood: str = Field(max_length=50, default="gentle")  # gentle, direct, playful, etc.
    ex_name: Optional[str] = Field(default=None, max_length=100)
    ex_personality_traits: Optional[str] = Field(
        default=None, max_length=500
    )  # JSON string
    relationship_context: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
