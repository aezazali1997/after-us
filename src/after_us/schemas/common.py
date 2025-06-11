from pydantic import BaseModel
from typing import Any, Optional


class StatusResponse(BaseModel):
    success: bool
    message: str


class ActivityResponse(BaseModel):
    id: int
    type: str
    description: str
    timestamp: str
    data: Optional[dict[str, Any]] = None
