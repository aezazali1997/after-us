from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import timedelta
from ..models.user import User
from ..schemas.auth import (
    UserRegistrationRequest,
    UserLoginRequest,
    AuthResponse,
    UserResponse,
)
from ..schemas.common import StatusResponse
from ..utils.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from ..utils.database import get_session
from ..services.healing_service import create_default_closure_activities

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse)
async def register(
    user_data: UserRegistrationRequest, session: Session = Depends(get_session)
):
    """Register a new user."""
    # Check if user already exists
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email, name=user_data.name, hashed_password=hashed_password
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Create default closure activities for the new user
    create_default_closure_activities(user, session)

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            is_active=user.is_active

        ),
        access_token=access_token,
    )


@router.post("/login", response_model=AuthResponse)
async def login(user_data: UserLoginRequest, session: Session = Depends(get_session)):
    """Login a user."""
    user = authenticate_user(user_data.email, user_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            is_active=user.is_active,
            profile_picture=user.profile_picture,
            ex_name=user.ex_name, 
            ex_picture=user.ex_picture,
            ex_nickname=user.ex_nickname,
        ),
        access_token=access_token,
    )


@router.post("/logout", response_model=StatusResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout a user."""
    # In a JWT-based system, logout is handled client-side by removing the token
    # This endpoint exists for consistency and future token blacklisting if needed
    return StatusResponse(success=True, message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
    )
