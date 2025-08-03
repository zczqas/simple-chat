from typing import List, Optional

from src.sc_chat.models.user import User


class UserRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID. Returns None if not found."""
        return self.db_session.query(User).filter(User.id == user_id).first()

    def get_users(self) -> List[User]:
        """Get all users."""
        return self.db_session.query(User).all()
