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
    profile_picture: Optional[str] = None
    ex_name: Optional[str] = None
    ex_picture:  Optional[str] = None
    ex_nickname: Optional[str] = None


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None

class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    profile_picture: Optional[str] = None
    ex_name: Optional[str] = None
    ex_picture: Optional[str] = None
    ex_nickname: Optional[str] = None

    class Config:
        orm_mode = True


class UserProfileResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool
    profile_picture: Optional[str] = None
    ex_name: Optional[str] = None
    ex_picture: Optional[str] = None
    ex_nickname: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
