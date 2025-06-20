from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict, Any
import json
import uuid
from ..models.user import User
from ..models.chat import ChatSession, ParsedMessage
from ..models.healing import AIPersonality
from ..schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    StartHealingSessionRequest,
    HealingSessionResponse,
)
from ..schemas.chat import ChatInsightsResponse
from ..utils.auth import get_current_user
from ..utils.database import get_session

router = APIRouter(prefix="/ai", tags=["AI"])


def generate_ai_response(
    message: str,
    personality: AIPersonality = None,
    context_messages: List[ParsedMessage] = None,
) -> str:
    """Generate AI response based on user input and context."""
    # This is a simplified AI response generator
    # In a real implementation, this would integrate with an AI service like OpenAI GPT

    base_response = "I understand how you're feeling. "

    if personality:
        if personality.tone == "supportive":
            base_response += "Remember that healing takes time, and you're doing great by taking this step. "
        elif personality.tone == "empathetic":
            base_response += (
                "I can feel the emotion in your words, and that's completely valid. "
            )
        elif personality.tone == "challenging":
            base_response += "Let's think about this differently - what would your stronger self do? "

    # Simple keyword-based responses
    message_lower = message.lower()
    if any(word in message_lower for word in ["sad", "hurt", "pain"]):
        base_response += "It's natural to feel this way after a relationship ends. These feelings are part of the healing process."
    elif any(word in message_lower for word in ["angry", "mad", "furious"]):
        base_response += "Anger is often a secondary emotion that masks hurt. It's okay to feel angry, but let's explore what's underneath."
    elif any(word in message_lower for word in ["miss", "lonely", "alone"]):
        base_response += "Missing someone shows how much they meant to you. This feeling will soften with time."
    elif any(word in message_lower for word in ["future", "move on", "forward"]):
        base_response += "Looking forward is a positive sign. You're already on the path to healing and growth."
    else:
        base_response += (
            "Thank you for sharing that with me. Your feelings are valid and important."
        )

    return base_response


@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(
    chat_request: AIChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """AI chat conversation with user."""
    # Get user's AI personality settings
    personality = session.exec(
        select(AIPersonality).where(AIPersonality.user_id == current_user.id)
    ).first()

    context_messages = None
    if chat_request.context_session_id:
        # Get context from specific chat session
        context_messages = session.exec(
            select(ParsedMessage)
            .where(ParsedMessage.session_id == chat_request.context_session_id)
            .limit(10)  # Last 10 messages for context
        ).all()

    # Generate AI response
    ai_response = generate_ai_response(
        chat_request.message, personality, context_messages
    )

    # Analyze emotion (simplified)
    emotion = None
    message_lower = chat_request.message.lower()
    if any(word in message_lower for word in ["sad", "hurt", "pain"]):
        emotion = "sad"
    elif any(word in message_lower for word in ["angry", "mad", "furious"]):
        emotion = "angry"
    elif any(word in message_lower for word in ["happy", "good", "better"]):
        emotion = "positive"
    elif any(word in message_lower for word in ["confused", "lost", "don't know"]):
        emotion = "confused"

    # Suggest actions based on emotion
    suggested_actions = []
    if emotion == "sad":
        suggested_actions = [
            "Practice self-compassion",
            "Write in a journal",
            "Take a walk in nature",
        ]
    elif emotion == "angry":
        suggested_actions = [
            "Try deep breathing exercises",
            "Do some physical exercise",
            "Write an unsent letter",
        ]
    elif emotion == "confused":
        suggested_actions = [
            "List your feelings",
            "Talk to a trusted friend",
            "Consider professional counseling",
        ]

    context_used = {}
    if context_messages:
        context_used = {
            "session_id": chat_request.context_session_id,
            "messages_analyzed": len(context_messages),
        }

    return AIChatResponse(
        response=ai_response,
        emotion=emotion,
        suggested_actions=suggested_actions,
        context_used=context_used,
    )


@router.get("/insights/{session_id}", response_model=ChatInsightsResponse)
async def get_chat_insights(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get AI-generated insights about the relationship from chat data."""
    # Verify session belongs to user
    chat_session = session.exec(
        select(ChatSession).where(
            ChatSession.id == session_id, ChatSession.user_id == current_user.id
        )
    ).first()

    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    # Get messages from the session
    messages = session.exec(
        select(ParsedMessage).where(ParsedMessage.session_id == session_id)
    ).all()

    if not messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages found in session",
        )

    # Analyze messages for insights (simplified analysis)
    user_messages = [msg for msg in messages if msg.is_user]
    partner_messages = [msg for msg in messages if not msg.is_user]

    # Calculate relationship duration
    first_message = min(messages, key=lambda m: m.timestamp)
    last_message = max(messages, key=lambda m: m.timestamp)
    duration = last_message.timestamp - first_message.timestamp
    relationship_duration = f"{duration.days} days"

    # Analyze communication patterns
    total_messages = len(messages)
    user_message_count = len(user_messages)
    partner_message_count = len(partner_messages)

    communication_patterns = {
        "total_messages": str(total_messages),
        "user_percentage": f"{(user_message_count / total_messages * 100):.1f}%",
        "partner_percentage": f"{(partner_message_count / total_messages * 100):.1f}%",
        "messages_per_day": f"{total_messages / max(duration.days, 1):.1f}",
    }

    # Simple sentiment analysis
    positive_words = ["love", "happy", "great", "amazing", "wonderful", "perfect"]
    negative_words = ["sad", "angry", "hate", "terrible", "awful", "horrible"]

    positive_score = 0
    negative_score = 0
    neutral_score = 0

    for message in messages:
        content_lower = message.content.lower()
        has_positive = any(word in content_lower for word in positive_words)
        has_negative = any(word in content_lower for word in negative_words)

        if has_positive and not has_negative:
            positive_score += 1
        elif has_negative and not has_positive:
            negative_score += 1
        else:
            neutral_score += 1

    total_analyzed = positive_score + negative_score + neutral_score
    emotional_tone = {
        "positive": positive_score / total_analyzed if total_analyzed > 0 else 0,
        "negative": negative_score / total_analyzed if total_analyzed > 0 else 0,
        "neutral": neutral_score / total_analyzed if total_analyzed > 0 else 0,
    }

    # Extract key themes (simplified keyword extraction)
    all_text = " ".join([msg.content for msg in messages]).lower()
    theme_keywords = {
        "love": ["love", "romantic", "relationship", "together"],
        "conflict": ["fight", "argue", "angry", "disagree"],
        "future": ["future", "plans", "tomorrow", "next"],
        "family": ["family", "parents", "mom", "dad"],
        "work": ["work", "job", "career", "office"],
    }

    key_themes = []
    for theme, keywords in theme_keywords.items():
        if any(keyword in all_text for keyword in keywords):
            key_themes.append(theme)

    # Calculate relationship health score (simplified)
    health_score = (
        emotional_tone["positive"] * 100
        + (1 - abs(0.5 - user_message_count / total_messages)) * 50
    )
    health_score = min(100, max(0, health_score))

    # Generate recommendations
    recommendations = []
    if emotional_tone["negative"] > 0.4:
        recommendations.append(
            "Focus on processing negative emotions through journaling or therapy"
        )
    if emotional_tone["positive"] > 0.6:
        recommendations.append(
            "Cherish the positive memories while allowing yourself to move forward"
        )
    if abs(user_message_count - partner_message_count) > total_messages * 0.3:
        recommendations.append(
            "Reflect on communication balance in future relationships"
        )

    recommendations.append(
        "Practice self-care and be patient with your healing process"
    )

    return ChatInsightsResponse(
        session_id=session_id,
        relationship_duration=relationship_duration,
        communication_patterns=communication_patterns,
        emotional_tone=emotional_tone,
        key_themes=key_themes,
        relationship_health_score=round(health_score, 1),
        recommendations=recommendations,
    )


@router.post("/healing-session", response_model=HealingSessionResponse)
async def start_healing_session(
    session_request: StartHealingSessionRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Start an AI-guided healing conversation session."""
    session_id = str(uuid.uuid4())

    # Get user's AI personality
    personality = session.exec(
        select(AIPersonality).where(AIPersonality.user_id == current_user.id)
    ).first()

    # Generate session-specific response based on type
    session_responses = {
        "general": "Welcome to your healing session. I'm here to support you through this journey. How are you feeling today?",
        "grief": "Grief is a natural response to loss. Let's take this slowly and honor your feelings. What aspect of your loss would you like to explore?",
        "anger": "Anger can be a powerful emotion that often masks deeper feelings. It's safe to express your anger here. What's making you feel angry right now?",
        "acceptance": "Acceptance is a beautiful stage of healing. It doesn't mean forgetting, but rather finding peace. What does acceptance mean to you right now?",
        "moving_forward": "Moving forward takes courage. You're showing strength by being here. What does your ideal future look like?",
    }

    ai_response = session_responses.get(
        session_request.session_type, session_responses["general"]
    )

    # Add personality-based modification
    if personality and personality.tone == "gentle":
        ai_response = "Gently, " + ai_response.lower()
    elif personality and personality.tone == "direct":
        ai_response = "Let's be direct: " + ai_response

    # Generate exercises based on session type
    exercises = []
    if session_request.session_type == "grief":
        exercises = [
            {"type": "writing", "description": "Write a letter to your past self"},
            {
                "type": "mindfulness",
                "description": "Practice 5-minute breathing meditation",
            },
            {
                "type": "reflection",
                "description": "List three things you learned from this relationship",
            },
        ]
    elif session_request.session_type == "anger":
        exercises = [
            {"type": "physical", "description": "Try intense exercise or boxing"},
            {"type": "writing", "description": "Write an angry letter (don't send it)"},
            {
                "type": "creative",
                "description": "Express your anger through art or music",
            },
        ]
    elif session_request.session_type == "acceptance":
        exercises = [
            {"type": "gratitude", "description": "List things you're grateful for"},
            {"type": "visualization", "description": "Visualize your peaceful future"},
            {
                "type": "affirmation",
                "description": "Practice self-compassion affirmations",
            },
        ]

    # Generate next steps
    next_steps = [
        "Take time to process today's session",
        "Practice one of the suggested exercises",
        "Journal about your feelings and insights",
        "Return when you're ready for the next step",
    ]

    return HealingSessionResponse(
        session_id=session_id,
        ai_response=ai_response,
        session_type=session_request.session_type,
        exercises=exercises,
        next_steps=next_steps,
    )
