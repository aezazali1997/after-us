from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, and_
from typing import List, Optional
from datetime import datetime, timedelta
from datetime import date as Date
from ..models.user import User
from ..models.healing import (
    NoContactDay,
    ClosureActivity,
    AIPersonality,
    ActivityCategory,
)
from ..schemas.healing import (
    CreateNoContactDayRequest,
    NoContactDayResponse,
    StreakResponse,
    UpdateClosureActivityRequest,
    ClosureActivityResponse,
    UpdateAIPersonalityRequest,
    AIPersonalityResponse,
)
from ..schemas.common import StatusResponse
from ..utils.auth import get_current_user
from ..utils.database import get_session

router = APIRouter(prefix="/healing", tags=["Healing"])


@router.get("/no-contact-days", response_model=List[NoContactDayResponse])
async def get_no_contact_days(
    start_date: Optional[Date] = Query(None),
    end_date: Optional[Date] = Query(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get user's no-contact tracking data."""
    query = select(NoContactDay).where(NoContactDay.user_id == current_user.id)

    if start_date:
        query = query.where(NoContactDay.date >= start_date)
    if end_date:
        query = query.where(NoContactDay.date <= end_date)

    no_contact_days = session.exec(query.order_by(NoContactDay.date.desc())).all()

    return [
        NoContactDayResponse(
            id=day.id,
            user_id=day.user_id,
            date=day.date,
            success=day.success,
            mood=day.mood,
            notes=day.notes,
            created_at=day.created_at,
        )
        for day in no_contact_days
    ]


@router.post("/no-contact-days", response_model=NoContactDayResponse)
async def create_no_contact_day(
    day_data: CreateNoContactDayRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a no-contact day entry."""
    # Check if entry already exists for this date
    existing_day = session.exec(
        select(NoContactDay).where(
            and_(
                NoContactDay.user_id == current_user.id,
                NoContactDay.date == day_data.date,
            )
        )
    ).first()

    if existing_day:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entry already exists for this date",
        )

    no_contact_day = NoContactDay(
        user_id=current_user.id,
        date=day_data.date,
        success=day_data.success,
        mood=day_data.mood,
        notes=day_data.notes,
    )

    session.add(no_contact_day)
    session.commit()
    session.refresh(no_contact_day)

    return NoContactDayResponse(
        id=no_contact_day.id,
        user_id=no_contact_day.user_id,
        date=no_contact_day.date,
        success=no_contact_day.success,
        mood=no_contact_day.mood,
        notes=no_contact_day.notes,
        created_at=no_contact_day.created_at,
    )


@router.get("/streak", response_model=StreakResponse)
async def get_streak_data(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get current and longest streak data."""
    no_contact_days = session.exec(
        select(NoContactDay)
        .where(NoContactDay.user_id == current_user.id)
        .order_by(NoContactDay.date.desc())
    ).all()

    if not no_contact_days:
        return StreakResponse(
            current_streak=0, longest_streak=0, total_days_tracked=0, success_rate=0.0
        )

    # Calculate current streak
    current_streak = 0
    current_date = Date.today()

    for day in no_contact_days:
        if day.date == current_date and day.success:
            current_streak += 1
            current_date -= timedelta(days=1)
        elif day.date == current_date and not day.success:
            break
        elif day.date < current_date:
            # Gap in tracking
            break

    # Calculate longest streak
    longest_streak = 0
    temp_streak = 0
    prev_date = None

    for day in reversed(no_contact_days):  # Process in chronological order
        if prev_date is None or day.date == prev_date + timedelta(days=1):
            if day.success:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 0
        else:
            temp_streak = 1 if day.success else 0

        prev_date = day.date

    # Calculate success rate
    total_days = len(no_contact_days)
    successful_days = sum(1 for day in no_contact_days if day.success)
    success_rate = (successful_days / total_days) * 100 if total_days > 0 else 0.0

    return StreakResponse(
        current_streak=current_streak,
        longest_streak=longest_streak,
        total_days_tracked=total_days,
        success_rate=round(success_rate, 2),
    )


@router.get("/closure-activities", response_model=List[ClosureActivityResponse])
async def get_closure_activities(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get user's closure activities."""
    activities = session.exec(
        select(ClosureActivity)
        .where(ClosureActivity.user_id == current_user.id)
        .order_by(ClosureActivity.created_at.desc())
    ).all()

    return [
        ClosureActivityResponse(
            id=activity.id,
            user_id=activity.user_id,
            title=activity.title,
            description=activity.description,
            completed=activity.completed,
            completed_date=activity.completed_date,
            category=activity.category,
            created_at=activity.created_at,
        )
        for activity in activities
    ]


@router.put("/closure-activities/{activity_id}", response_model=ClosureActivityResponse)
async def update_closure_activity(
    activity_id: int,
    activity_data: UpdateClosureActivityRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update a closure activity status."""
    activity = session.exec(
        select(ClosureActivity).where(
            and_(
                ClosureActivity.id == activity_id,
                ClosureActivity.user_id == current_user.id,
            )
        )
    ).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Closure activity not found"
        )

    # Update fields if provided
    if activity_data.completed is not None:
        activity.completed = activity_data.completed
        if activity_data.completed and not activity.completed_date:
            activity.completed_date = datetime.utcnow()
        elif not activity_data.completed:
            activity.completed_date = None

    if activity_data.completed_date is not None:
        activity.completed_date = activity_data.completed_date

    session.add(activity)
    session.commit()
    session.refresh(activity)

    return ClosureActivityResponse(
        id=activity.id,
        user_id=activity.user_id,
        title=activity.title,
        description=activity.description,
        completed=activity.completed,
        completed_date=activity.completed_date,
        category=activity.category,
        created_at=activity.created_at,
    )


@router.get("/ai-personality", response_model=AIPersonalityResponse)
async def get_ai_personality(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get current AI ex personality settings."""
    personality = session.exec(
        select(AIPersonality).where(AIPersonality.user_id == current_user.id)
    ).first()

    if not personality:
        # Create default personality if none exists
        personality = AIPersonality(
            user_id=current_user.id, tone="supportive", mood="gentle"
        )
        session.add(personality)
        session.commit()
        session.refresh(personality)

    return AIPersonalityResponse(
        id=personality.id,
        user_id=personality.user_id,
        tone=personality.tone,
        mood=personality.mood,
        ex_name=personality.ex_name,
        ex_personality_traits=personality.ex_personality_traits,
        relationship_context=personality.relationship_context,
        created_at=personality.created_at,
        updated_at=personality.updated_at,
    )


@router.put("/ai-personality", response_model=AIPersonalityResponse)
async def update_ai_personality(
    personality_data: UpdateAIPersonalityRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update AI personality settings."""
    personality = session.exec(
        select(AIPersonality).where(AIPersonality.user_id == current_user.id)
    ).first()

    if not personality:
        # Create new personality if none exists
        personality = AIPersonality(
            user_id=current_user.id, tone="supportive", mood="gentle"
        )

    # Update fields if provided
    update_data = personality_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(personality, field, value)

    personality.updated_at = datetime.utcnow()
    session.add(personality)
    session.commit()
    session.refresh(personality)

    return AIPersonalityResponse(
        id=personality.id,
        user_id=personality.user_id,
        tone=personality.tone,
        mood=personality.mood,
        ex_name=personality.ex_name,
        ex_personality_traits=personality.ex_personality_traits,
        relationship_context=personality.relationship_context,
        created_at=personality.created_at,
        updated_at=personality.updated_at,
    )
