from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    password: str  # this will be hashed before storing

    class Config:
        orm_mode = True


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
