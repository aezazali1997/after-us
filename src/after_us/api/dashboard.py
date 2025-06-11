from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from typing import List, Dict, Any
from datetime import datetime, timedelta
from datetime import date as Date
from ..models.user import User
from ..models.chat import ChatSession, ParsedMessage
from ..models.memory import Memory
from ..models.healing import NoContactDay, ClosureActivity
from ..schemas.dashboard import DashboardStatsResponse
from ..schemas.common import ActivityResponse
from ..utils.auth import get_current_user
from ..utils.database import get_session

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get user dashboard statistics."""

    # Count chat sessions
    sessions_count = (
        session.exec(
            select(func.count(ChatSession.id)).where(
                ChatSession.user_id == current_user.id
            )
        ).first()
        or 0
    )

    # Count messages
    messages_count = (
        session.exec(
            select(func.count(ParsedMessage.id))
            .join(ChatSession)
            .where(ChatSession.user_id == current_user.id)
        ).first()
        or 0
    )

    # Count memories
    memories_count = (
        session.exec(
            select(func.count(Memory.id)).where(Memory.user_id == current_user.id)
        ).first()
        or 0
    )

    # Calculate no contact streak
    no_contact_days = session.exec(
        select(NoContactDay)
        .where(NoContactDay.user_id == current_user.id)
        .order_by(NoContactDay.date.desc())
    ).all()

    no_contact_streak = 0
    current_date = Date.today()

    for day in no_contact_days:
        if day.date == current_date and day.success:
            no_contact_streak += 1
            current_date -= timedelta(days=1)
        elif day.date == current_date and not day.success:
            break
        elif day.date < current_date:
            break

    # Count total healing days (no contact days tracked)
    total_healing_days = len(no_contact_days)

    # Count completed activities
    completed_activities = (
        session.exec(
            select(func.count(ClosureActivity.id))
            .where(ClosureActivity.user_id == current_user.id)
            .where(ClosureActivity.completed == True)
        ).first()
        or 0
    )

    # Get last activity date
    last_memory = session.exec(
        select(Memory.created_at)
        .where(Memory.user_id == current_user.id)
        .order_by(Memory.created_at.desc())
    ).first()

    last_no_contact = session.exec(
        select(NoContactDay.created_at)
        .where(NoContactDay.user_id == current_user.id)
        .order_by(NoContactDay.created_at.desc())
    ).first()

    last_activity_dates = [d for d in [last_memory, last_no_contact] if d is not None]
    last_activity_date = (
        max(last_activity_dates).strftime("%Y-%m-%d") if last_activity_dates else "N/A"
    )

    # Mood distribution from no contact days
    mood_distribution: Dict[str, int] = {}
    for day in no_contact_days:
        if day.mood:
            mood_distribution[day.mood] = mood_distribution.get(day.mood, 0) + 1

    # Weekly progress (last 7 days of no contact tracking)
    week_ago = Date.today() - timedelta(days=7)
    recent_days = [day for day in no_contact_days if day.date >= week_ago]

    weekly_progress = {
        "days_tracked": len(recent_days),
        "successful_days": sum(1 for day in recent_days if day.success),
        "success_rate": (
            sum(1 for day in recent_days if day.success) / len(recent_days) * 100
        )
        if recent_days
        else 0,
    }

    return DashboardStatsResponse(
        sessions_count=sessions_count,
        messages_count=messages_count,
        memories_count=memories_count,
        no_contact_streak=no_contact_streak,
        total_healing_days=total_healing_days,
        completed_activities=completed_activities,
        last_activity_date=last_activity_date,
        mood_distribution=mood_distribution,
        weekly_progress=weekly_progress,
    )


@router.get("/recent-activity", response_model=List[ActivityResponse])
async def get_recent_activity(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get recent user activities."""
    activities = []

    # Get recent memories
    recent_memories = session.exec(
        select(Memory)
        .where(Memory.user_id == current_user.id)
        .order_by(Memory.created_at.desc())
        .limit(limit)
    ).all()

    for memory in recent_memories:
        activities.append(
            ActivityResponse(
                id=memory.id,
                type="memory",
                description=f"Created memory: {memory.title}",
                timestamp=memory.created_at.isoformat(),
                data={"memory_type": memory.type.value, "mood": memory.mood},
            )
        )

    # Get recent no contact days
    recent_no_contact = session.exec(
        select(NoContactDay)
        .where(NoContactDay.user_id == current_user.id)
        .order_by(NoContactDay.created_at.desc())
        .limit(limit)
    ).all()

    for day in recent_no_contact:
        status = "successful" if day.success else "failed"
        activities.append(
            ActivityResponse(
                id=day.id,
                type="no_contact",
                description=f"No contact day - {status}",
                timestamp=day.created_at.isoformat(),
                data={
                    "date": day.date.isoformat(),
                    "success": day.success,
                    "mood": day.mood,
                },
            )
        )

    # Get recent completed activities
    recent_completed = session.exec(
        select(ClosureActivity)
        .where(ClosureActivity.user_id == current_user.id)
        .where(ClosureActivity.completed == True)
        .order_by(ClosureActivity.completed_date.desc())
        .limit(limit)
    ).all()

    for activity in recent_completed:
        activities.append(
            ActivityResponse(
                id=activity.id,
                type="closure_activity",
                description=f"Completed activity: {activity.title}",
                timestamp=activity.completed_date.isoformat()
                if activity.completed_date
                else activity.created_at.isoformat(),
                data={
                    "category": activity.category.value,
                    "description": activity.description,
                },
            )
        )

    # Get recent chat sessions
    recent_sessions = session.exec(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.upload_date.desc())
        .limit(limit)
    ).all()

    for chat_session in recent_sessions:
        activities.append(
            ActivityResponse(
                id=chat_session.id,
                type="chat_upload",
                description=f"Uploaded chat: {chat_session.filename}",
                timestamp=chat_session.upload_date.isoformat(),
                data={
                    "total_messages": chat_session.total_messages,
                    "participants": chat_session.participants,
                },
            )
        )

    # Sort all activities by timestamp and return the most recent ones
    activities.sort(key=lambda x: x.timestamp, reverse=True)

    return activities[:limit]
