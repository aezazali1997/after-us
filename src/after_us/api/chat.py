from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session, select
import re
from typing import List
import json
import re
from datetime import datetime
from ..models.user import User
from ..models.chat import ChatSession, ParsedMessage
from ..schemas.chat import (
    ChatSessionResponse,
    ChatSessionDetailResponse,
    ParsedMessageResponse,
    ChatInsightsResponse,
)
from ..schemas.common import StatusResponse
from ..utils.auth import get_current_user
from ..utils.database import get_session

router = APIRouter(prefix="/chat", tags=["Chat"])


def parse_whatsapp_export(content: str, user_name: str) -> List[dict]:
    messages = []
    lines = content.split("\n")

    # WhatsApp format: [DD/MM/YYYY, HH:MM AM/PM] Name: Message
    pattern = r"(\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}(?::\d{2})?\s*[APMapm]{2})\s*-\s*([^:]+):\s*(.+)"

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(pattern, line)
        if match:
            timestamp_str, sender, message_content = match.groups()

            # Normalize unicode whitespace characters
            timestamp_str = re.sub(r'\s+', ' ', timestamp_str).strip()

            # Parse timestamp
            try:
                if timestamp_str.count(":") == 2:
                    timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y, %I:%M:%S %p")
                else:
                    timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y, %I:%M %p")
            except ValueError:
                continue  # Skip badly formatted timestamps

            is_user = sender.strip() == user_name.strip()

            messages.append(
                {
                    "timestamp": timestamp,
                    "sender": sender.strip(),
                    "content": message_content.strip(),
                    "is_user": is_user,
                }
            )


    return messages
@router.post("/upload", response_model=ChatSessionResponse)
async def upload_chat(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Upload and process WhatsApp chat export file."""
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt files are supported",
        )

    try:
        content = await file.read()
        text_content = content.decode("utf-8")


        # Parse messages
        parsed_messages = parse_whatsapp_export(text_content, current_user.name)


        if not parsed_messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid messages found in the file",
            )

        # Extract participants
        participants = list(set(msg["sender"] for msg in parsed_messages))

        # Create chat session
        chat_session = ChatSession(
            user_id=current_user.id,
            filename=file.filename,
            total_messages=len(parsed_messages),
            participants=json.dumps(participants),
        )

        session.add(chat_session)
        session.commit()
        session.refresh(chat_session)

        # Add messages
        for msg_data in parsed_messages:
            message = ParsedMessage(
                session_id=chat_session.id,
                timestamp=msg_data["timestamp"],
                sender=msg_data["sender"],
                content=msg_data["content"],
                is_user=msg_data["is_user"],
            )
            session.add(message)

        session.commit()

        return ChatSessionResponse(
            id=chat_session.id,
            user_id=chat_session.user_id,
            filename=chat_session.filename,
            upload_date=chat_session.upload_date,
            total_messages=chat_session.total_messages,
            participants=chat_session.participants,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}",
        )


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get user's chat sessions."""
    sessions_query = (
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .offset(offset)
        .limit(limit)
    )

    chat_sessions = session.exec(sessions_query).all()

    return [
        ChatSessionResponse(
            id=cs.id,
            user_id=cs.user_id,
            filename=cs.filename,
            upload_date=cs.upload_date,
            total_messages=cs.total_messages,
            participants=cs.participants,
        )
        for cs in chat_sessions
    ]


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailResponse)
async def get_chat_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get full chat session with all messages."""
    chat_session = session.exec(
        select(ChatSession).where(
            ChatSession.id == session_id, ChatSession.user_id == current_user.id
        )
    ).first()

    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    messages = session.exec(
        select(ParsedMessage).where(ParsedMessage.session_id == session_id)
    ).all()

    return ChatSessionDetailResponse(
        id=chat_session.id,
        user_id=chat_session.user_id,
        filename=chat_session.filename,
        upload_date=chat_session.upload_date,
        total_messages=chat_session.total_messages,
        participants=chat_session.participants,
        messages=[
            ParsedMessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                timestamp=msg.timestamp,
                sender=msg.sender,
                content=msg.content,
                is_user=msg.is_user,
            )
            for msg in messages
        ],
    )


@router.delete("/sessions/{session_id}", response_model=StatusResponse)
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a chat session."""
    chat_session = session.exec(
        select(ChatSession).where(
            ChatSession.id == session_id, ChatSession.user_id == current_user.id
        )
    ).first()

    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    # Delete associated messages first
    messages = session.exec(
        select(ParsedMessage).where(ParsedMessage.session_id == session_id)
    ).all()

    for message in messages:
        session.delete(message)

    session.delete(chat_session)
    session.commit()

    return StatusResponse(success=True, message="Chat session deleted successfully")


@router.get(
    "/sessions/{session_id}/messages", response_model=List[ParsedMessageResponse]
)
async def get_session_messages(
    session_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get paginated messages from a chat session."""
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

    messages = session.exec(
        select(ParsedMessage)
        .where(ParsedMessage.session_id == session_id)
        .offset(offset)
        .limit(limit)
    ).all()

    return [
        ParsedMessageResponse(
            id=msg.id,
            session_id=msg.session_id,
            timestamp=msg.timestamp,
            sender=msg.sender,
            content=msg.content,
            is_user=msg.is_user,
        )
        for msg in messages
    ]
