from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
    is_active: bool


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
