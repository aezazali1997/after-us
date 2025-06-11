from pydantic import BaseModel
from typing import List, Dict, Any


class DashboardStatsResponse(BaseModel):
    sessions_count: int
    messages_count: int
    memories_count: int
    no_contact_streak: int
    total_healing_days: int
    completed_activities: int
    last_activity_date: str
    mood_distribution: Dict[str, int]
    weekly_progress: Dict[str, Any]
