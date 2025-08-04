from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.sc_chat.database.conn import get_db
from src.sc_chat.repository.chat_repository import ChatRepository
from src.sc_chat.schemas.chat import RoomResponse, RoomCreate, MessageResponse
from src.sc_chat.security.rbac import require_user, require_admin
from src.sc_chat.models.user import User

router = APIRouter(prefix="/rooms", tags=["Chat Rooms"])


def get_chat_repository(db: Session = Depends(get_db)) -> ChatRepository:
    """Dependency to get chat repository instance."""
    return ChatRepository(db)


@router.get("/", response_model=List[RoomResponse])
def get_all_rooms(
    chat_repo: ChatRepository = Depends(get_chat_repository),
    current_user: User = Depends(require_user()),
):
    """Get all active chat rooms."""
    rooms = chat_repo.get_all_rooms()
    return rooms


@router.post("/", response_model=RoomResponse)
def create_room(
    room_data: RoomCreate,
    chat_repo: ChatRepository = Depends(get_chat_repository),
    current_user: User = Depends(require_admin()),
):
    """Create a new chat room (Admin only)."""
    existing_room = chat_repo.get_room_by_name(room_data.name)
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room with name '{room_data.name}' already exists",
        )

    room = chat_repo.create_room(name=room_data.name, description=room_data.description)
    return room


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    chat_repo: ChatRepository = Depends(get_chat_repository),
    current_user: User = Depends(require_user()),
):
    """Get a specific room by ID."""
    room = chat_repo.get_room_by_id(room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found",
        )
    return room


@router.get("/{room_id}/messages", response_model=List[MessageResponse])
def get_room_messages(
    room_id: int,
    limit: int = 50,
    cursor: int | None = None,
    chat_repo: ChatRepository = Depends(get_chat_repository),
    current_user: User = Depends(require_user()),
):
    """
    Get messages from a room with pagination.

    Use this endpoint to fetch message history via REST API.
    For real-time messaging, use the WebSocket endpoint /ws/{room_id}
    """
    room = chat_repo.get_room_by_id(room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found",
        )

    messages, has_more = chat_repo.get_recent_messages(room_id, limit, cursor)
    return messages
