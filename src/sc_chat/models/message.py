from sqlalchemy import Column, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.sc_chat.database.base import Base
from src.sc_chat.models.base import TimestampMixin


class Message(Base, TimestampMixin):
    """
    Message model for chat messages.
    """

    __tablename__ = "messages"

    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)

    user = relationship("User", back_populates="messages")
    room = relationship("Room", back_populates="messages")

    def __repr__(self):
        return (
            f"<Message(id={self.id}, user_id={self.user_id}, room_id={self.room_id})>"
        )
