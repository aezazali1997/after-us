from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    profile_picture: Optional[str] = Field(default=None, max_length=255)
    ex_name: Optional[str] = Field(default=None, max_length=255)
    ex_picture: Optional[str] = Field(default=None, max_length=255)
    ex_nickname: Optional[str] = Field(default=None, max_length=255)

