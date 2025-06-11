from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List


class ChatSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    filename: str = Field(max_length=255)
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    total_messages: int = Field(default=0)
    participants: str = Field(max_length=500)  # JSON string of participant names

    # Relationship to messages
    messages: List["ParsedMessage"] = Relationship(back_populates="session")


class ParsedMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chatsession.id", index=True)
    timestamp: datetime
    sender: str = Field(max_length=100)
    content: str = Field(max_length=5000)
    is_user: bool = Field(default=False)  # True if message is from the app user

    # Relationship to session
    session: Optional[ChatSession] = Relationship(back_populates="messages")
