from pydantic import BaseModel
from datetime import datetime
from datetime import date as Date
from typing import Optional
from ..models.healing import ActivityCategory


class CreateNoContactDayRequest(BaseModel):
    date: Date
    success: bool = True
    mood: Optional[str] = None
    notes: Optional[str] = None


class NoContactDayResponse(BaseModel):
    id: int
    user_id: int
    date: Date
    success: bool
    mood: Optional[str]
    notes: Optional[str]
    created_at: datetime


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    total_days_tracked: int
    success_rate: float


class UpdateClosureActivityRequest(BaseModel):
    completed: Optional[bool] = None
    completed_date: Optional[datetime] = None


class ClosureActivityResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    completed: bool
    completed_date: Optional[datetime]
    category: ActivityCategory
    created_at: datetime


class UpdateAIPersonalityRequest(BaseModel):
    tone: Optional[str] = None
    mood: Optional[str] = None
    ex_name: Optional[str] = None
    ex_personality_traits: Optional[str] = None
    relationship_context: Optional[str] = None


class AIPersonalityResponse(BaseModel):
    id: int
    user_id: int
    tone: str
    mood: str
    ex_name: Optional[str]
    ex_personality_traits: Optional[str]
    relationship_context: Optional[str]
    created_at: datetime
    updated_at: datetime
