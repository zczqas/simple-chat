from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from src.sc_chat.schemas.user import UserResponse


class RoomBase(BaseModel):
    """Base room schema with common fields."""

    name: str
    description: Optional[str] = None


class RoomCreate(RoomBase):
    """Schema for creating a room."""

    pass


class RoomUpdate(BaseModel):
    """Schema for updating a room."""

    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoomResponse(RoomBase):
    """Schema for room response."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    """Base message schema with common fields."""

    content: str


class MessageCreate(MessageBase):
    """Schema for creating a message."""

    room_id: int


class MessageResponse(MessageBase):
    """Schema for message response."""

    id: int
    user_id: int
    room_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    """Schema for real-time chat message response."""

    id: int
    content: str
    user_id: int
    username: str
    room_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedMessagesResponse(BaseModel):
    """Schema for paginated messages response."""

    messages: List[ChatMessageResponse]
    has_more: bool
    next_cursor: Optional[int] = None
