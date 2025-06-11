from sqlmodel import Session, select
from ..models.healing import ClosureActivity, ActivityCategory
from ..models.user import User


def create_default_closure_activities(user: User, session: Session) -> None:
    """Create default closure activities for a new user."""

    # Check if user already has activities
    existing_activities = session.exec(
        select(ClosureActivity).where(ClosureActivity.user_id == user.id)
    ).first()

    if existing_activities:
        return  # User already has activities

    # Default closure activities
    default_activities = [
        {
            "title": "Write a letter to yourself",
            "description": "Write a compassionate letter to yourself about your healing journey. Acknowledge your progress and be kind to yourself.",
            "category": ActivityCategory.EMOTIONAL,
        },
        {
            "title": "Create a self-care routine",
            "description": "Establish a daily routine that includes activities that make you feel good about yourself and your life.",
            "category": ActivityCategory.SELF_CARE,
        },
        {
            "title": "Start a new hobby",
            "description": "Pick up a new hobby or return to an old one that brings you joy and helps you meet new people.",
            "category": ActivityCategory.CREATIVE,
        },
        {
            "title": "Exercise regularly",
            "description": "Commit to regular physical activity to improve your mood and overall health. Even a daily walk counts!",
            "category": ActivityCategory.PHYSICAL,
        },
        {
            "title": "Connect with friends",
            "description": "Reach out to friends and family members. Plan social activities and strengthen your support network.",
            "category": ActivityCategory.SOCIAL,
        },
        {
            "title": "Practice mindfulness",
            "description": "Incorporate mindfulness practices like meditation, deep breathing, or yoga into your daily routine.",
            "category": ActivityCategory.EMOTIONAL,
        },
        {
            "title": "Set new goals",
            "description": "Identify new personal or professional goals to work towards. Having something to look forward to helps with healing.",
            "category": ActivityCategory.PROFESSIONAL,
        },
        {
            "title": "Declutter your space",
            "description": "Organize and declutter your living space. A clean environment can help clear your mind and represent a fresh start.",
            "category": ActivityCategory.SELF_CARE,
        },
        {
            "title": "Learn something new",
            "description": "Take a class, read books, or learn a new skill. Personal growth helps build confidence and creates new opportunities.",
            "category": ActivityCategory.CREATIVE,
        },
        {
            "title": "Volunteer for a cause",
            "description": "Find a cause you care about and volunteer your time. Helping others can provide perspective and purpose.",
            "category": ActivityCategory.SOCIAL,
        },
    ]

    # Create activities for the user
    for activity_data in default_activities:
        activity = ClosureActivity(
            user_id=user.id,
            title=activity_data["title"],
            description=activity_data["description"],
            category=activity_data["category"],
        )
        session.add(activity)

    session.commit()
