from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc

from src.sc_chat.models.room import Room
from src.sc_chat.models.message import Message


class ChatRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    # Room operations
    def create_room(self, name: str, description: Optional[str] = None) -> Room:
        """Create a new chat room."""
        room = Room(name=name, description=description)
        self.db_session.add(room)
        self.db_session.commit()
        self.db_session.refresh(room)
        return room

    def get_room_by_id(self, room_id: int) -> Optional[Room]:
        """Get a room by ID."""
        return (
            self.db_session.query(Room)
            .filter(Room.id == room_id, Room.is_active.is_(True))
            .first()
        )

    def get_room_by_name(self, name: str) -> Optional[Room]:
        """Get a room by name."""
        return (
            self.db_session.query(Room)
            .filter(Room.name == name, Room.is_active.is_(True))
            .first()
        )

    def get_all_rooms(self) -> List[Room]:
        """Get all active rooms."""
        return self.db_session.query(Room).filter(Room.is_active.is_(True)).all()

    # Message operations
    def create_message(self, content: str, user_id: int, room_id: int) -> Message:
        """Create a new message in a room."""
        message = Message(content=content, user_id=user_id, room_id=room_id)
        self.db_session.add(message)
        self.db_session.commit()
        self.db_session.refresh(message)
        return message

    def get_recent_messages(
        self, room_id: int, limit: int = 50, cursor: Optional[int] = None
    ) -> tuple[List[Message], bool]:
        """
        Get recent messages for a room with cursor-based pagination.

        Args:
            room_id: The room ID to fetch messages from
            limit: Maximum number of messages to return
            cursor: Optional cursor for pagination (message ID to start from)

        Returns:
            Tuple of (messages, has_more) where has_more indicates if there are more messages
        """
        query = (
            self.db_session.query(Message)
            .options(joinedload(Message.user))
            .filter(Message.room_id == room_id)
            .order_by(desc(Message.id))
        )

        if cursor:
            query = query.filter(Message.id < cursor)

        # Fetch one extra message to check if there are more
        messages = query.limit(limit + 1).all()

        has_more = len(messages) > limit
        if has_more:
            messages = messages[:limit]

        # Return messages in chronological order (oldest first)
        return list(reversed(messages)), has_more

    def get_message_by_id(self, message_id: int) -> Optional[Message]:
        """Get a message by ID with user information."""
        return (
            self.db_session.query(Message)
            .options(joinedload(Message.user))
            .filter(Message.id == message_id)
            .first()
        )

    def delete_message(self, message_id: int, user_id: int) -> bool:
        """Delete a message (only by the message author or admin)."""
        message = (
            self.db_session.query(Message)
            .filter(Message.id == message_id, Message.user_id == user_id)
            .first()
        )

        if message:
            self.db_session.delete(message)
            self.db_session.commit()
            return True
        return False
