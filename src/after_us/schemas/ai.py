from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class AIChatRequest(BaseModel):
    message: str
    context_session_id: Optional[int] = None  # For context from specific chat session
    personality_mode: Optional[str] = None  # Override default personality


class AIChatResponse(BaseModel):
    response: str
    emotion: Optional[str] = None
    suggested_actions: Optional[List[str]] = None
    context_used: Optional[Dict[str, Any]] = None


class StartHealingSessionRequest(BaseModel):
    session_type: str = "general"  # general, grief, anger, acceptance, etc.
    mood: Optional[str] = None
    specific_topic: Optional[str] = None


class HealingSessionResponse(BaseModel):
    session_id: str
    ai_response: str
    session_type: str
    exercises: Optional[List[Dict[str, str]]] = None
    next_steps: Optional[List[str]] = None
