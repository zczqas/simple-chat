from typing import Optional

from sqlalchemy.orm import Session

from src.sc_chat.models.user import User
from src.sc_chat.security.auth import jwt_service


class AuthRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email. Returns None if not found."""
        return self.db_session.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username. Returns None if not found."""
        return self.db_session.query(User).filter(User.username == username).first()

    def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user with hashed password."""
        hashed_password = jwt_service.get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
        )
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password. Returns user if valid, None otherwise."""
        try:
            return jwt_service.authenticate_user(email, password, self.db_session)
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return None

    def user_exists_by_email(self, email: str) -> bool:
        """Check if a user exists by email."""
        return (
            self.db_session.query(User).filter(User.email == email).first() is not None
        )

    def user_exists_by_username(self, username: str) -> bool:
        """Check if a user exists by username."""
        return (
            self.db_session.query(User).filter(User.username == username).first()
            is not None
        )

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID. Returns None if not found."""
        return self.db_session.query(User).filter(User.id == user_id).first()

    def deactivate_user(self, user: User) -> User:
        """Deactivate a user account."""
        self.db_session.query(User).filter(User.id == user.id).update(
            {"is_active": False}
        )
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def activate_user(self, user: User) -> User:
        """Activate a user account."""
        self.db_session.query(User).filter(User.id == user.id).update(
            {"is_active": True}
        )
        self.db_session.commit()
        self.db_session.refresh(user)
        return user
