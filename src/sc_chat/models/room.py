from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship

from src.sc_chat.database.base import Base
from src.sc_chat.models.base import TimestampMixin


class Room(Base, TimestampMixin):
    """
    Room model for chat rooms.
    """

    __tablename__ = "rooms"

    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    messages = relationship(
        "Message", back_populates="room", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Room(id={self.id}, name='{self.name}')>"
