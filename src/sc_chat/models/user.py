from sqlalchemy import Column, Boolean, String
from sqlalchemy import Enum as SQLAlchemyEnum

from src.sc_chat.database.base import Base
from src.sc_chat.models.base import TimestampMixin
from src.sc_chat.utils.common.enum import UserRoleEnum


class User(Base, TimestampMixin):
    """
    User model that inherits from TimestampMixin.
    This model represents a user in the system with additional fields.
    """

    __tablename__ = "users"

    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(
        SQLAlchemyEnum(UserRoleEnum),
        default=UserRoleEnum.USER,
        nullable=False,
    )
