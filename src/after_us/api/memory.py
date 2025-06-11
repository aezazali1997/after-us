from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from ..models.user import User
from ..models.memory import Memory, MemoryType
from ..models.chat import ChatSession, ParsedMessage
from ..schemas.memory import CreateMemoryRequest, UpdateMemoryRequest, MemoryResponse
from ..schemas.common import StatusResponse
from ..utils.auth import get_current_user
from ..utils.database import get_session

router = APIRouter(prefix="/memories", tags=["Memory"])


@router.get("", response_model=List[MemoryResponse])
async def get_memories(
    type: Optional[str] = Query(None, description="Filter by memory type"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get user's memories with optional filtering."""
    query = select(Memory).where(Memory.user_id == current_user.id)

    if type:
        try:
            memory_type = MemoryType(type)
            query = query.where(Memory.type == memory_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid memory type: {type}",
            )

    query = query.offset(offset).limit(limit)
    memories = session.exec(query).all()

    return [
        MemoryResponse(
            id=memory.id,
            user_id=memory.user_id,
            title=memory.title,
            description=memory.description,
            date=memory.date,
            type=memory.type,
            mood=memory.mood,
            participants=memory.participants,
            image_url=memory.image_url,
            created_at=memory.created_at,
            updated_at=memory.updated_at,
        )
        for memory in memories
    ]


@router.post("", response_model=MemoryResponse)
async def create_memory(
    memory_data: CreateMemoryRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new memory."""
    memory = Memory(
        user_id=current_user.id,
        title=memory_data.title,
        description=memory_data.description,
        date=memory_data.date,
        type=memory_data.type,
        mood=memory_data.mood,
        participants=memory_data.participants,
        image_url=memory_data.image_url,
    )

    session.add(memory)
    session.commit()
    session.refresh(memory)

    return MemoryResponse(
        id=memory.id,
        user_id=memory.user_id,
        title=memory.title,
        description=memory.description,
        date=memory.date,
        type=memory.type,
        mood=memory.mood,
        participants=memory.participants,
        image_url=memory.image_url,
        created_at=memory.created_at,
        updated_at=memory.updated_at,
    )


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: int,
    memory_data: UpdateMemoryRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update an existing memory."""
    memory = session.exec(
        select(Memory).where(Memory.id == memory_id, Memory.user_id == current_user.id)
    ).first()

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found"
        )

    # Update fields if provided
    update_data = memory_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(memory, field, value)

    memory.updated_at = datetime.utcnow()
    session.add(memory)
    session.commit()
    session.refresh(memory)

    return MemoryResponse(
        id=memory.id,
        user_id=memory.user_id,
        title=memory.title,
        description=memory.description,
        date=memory.date,
        type=memory.type,
        mood=memory.mood,
        participants=memory.participants,
        image_url=memory.image_url,
        created_at=memory.created_at,
        updated_at=memory.updated_at,
    )


@router.delete("/{memory_id}", response_model=StatusResponse)
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a memory."""
    memory = session.exec(
        select(Memory).where(Memory.id == memory_id, Memory.user_id == current_user.id)
    ).first()

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found"
        )

    session.delete(memory)
    session.commit()

    return StatusResponse(success=True, message="Memory deleted successfully")


@router.post("/extract/{session_id}", response_model=List[MemoryResponse])
async def extract_memories_from_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Extract memories from a chat session using AI analysis."""
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
        return []

    # Simple memory extraction based on keywords and patterns
    # In a real implementation, this would use AI/NLP for better extraction
    extracted_memories = []

    # Look for potential memory indicators
    memory_keywords = {
        "first": MemoryType.FIRST_MEETING,
        "meet": MemoryType.FIRST_MEETING,
        "anniversary": MemoryType.MILESTONE,
        "birthday": MemoryType.MILESTONE,
        "fight": MemoryType.CONFLICT,
        "argue": MemoryType.CONFLICT,
        "last": MemoryType.LAST_CONTACT,
        "goodbye": MemoryType.LAST_CONTACT,
        "sweet": MemoryType.SWEET_MOMENT,
        "love": MemoryType.SWEET_MOMENT,
    }

    for message in messages:
        content_lower = message.content.lower()
        for keyword, memory_type in memory_keywords.items():
            if keyword in content_lower and len(message.content) > 50:
                # Create a memory from this message
                memory = Memory(
                    user_id=current_user.id,
                    title=f"Memory from {message.timestamp.strftime('%Y-%m-%d')}",
                    description=message.content[:500],  # Truncate if too long
                    date=message.timestamp.date(),
                    type=memory_type,
                    participants=chat_session.participants,
                )

                session.add(memory)
                extracted_memories.append(memory)
                break  # Only create one memory per message

    if extracted_memories:
        session.commit()
        # Refresh all memories to get their IDs
        for memory in extracted_memories:
            session.refresh(memory)

    return [
        MemoryResponse(
            id=memory.id,
            user_id=memory.user_id,
            title=memory.title,
            description=memory.description,
            date=memory.date,
            type=memory.type,
            mood=memory.mood,
            participants=memory.participants,
            image_url=memory.image_url,
            created_at=memory.created_at,
            updated_at=memory.updated_at,
        )
        for memory in extracted_memories
    ]
