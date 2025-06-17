from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime



router = APIRouter(prefix="/users", tags=["User Management"])
from ..models.user import User
from ..schemas.user import (
    UserResponse,
    CreateUserRequest,
    UpdateUserRequest,
    UserProfileResponse,
)
from ..schemas.common import StatusResponse
from ..utils.auth import get_current_user
from ..utils.database import get_session

@router.patch("/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(
    user_id: int,
    user_data: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    print('id', current_user.id)
    """Update a user's profile."""
    user = session.exec(
        select(User).where(User.id == user_id, User.id == current_user.id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update fields if provided
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)

    return UserProfileResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        is_active=user.is_active,
        profile_picture=user.profile_picture,
        ex_name=user.ex_name, 
        ex_picture=user.ex_picture,
        ex_nickname=user.ex_nickname,
    )