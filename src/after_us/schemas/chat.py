from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ParsedMessageResponse(BaseModel):
    id: int
    session_id: int
    timestamp: datetime
    sender: str
    content: str
    is_user: bool


class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    upload_date: datetime
    total_messages: int
    participants: str
    messages: Optional[List[ParsedMessageResponse]] = None


class ChatSessionDetailResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    upload_date: datetime
    total_messages: int
    participants: str
    messages: List[ParsedMessageResponse]


class ChatInsightsResponse(BaseModel):
    session_id: int
    relationship_duration: Optional[str] = None
    communication_patterns: dict[str, str]
    emotional_tone: dict[str, float]  # sentiment analysis scores
    key_themes: List[str]
    relationship_health_score: Optional[float] = None
    recommendations: List[str]
