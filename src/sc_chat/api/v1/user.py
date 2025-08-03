from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.sc_chat.security.auth import jwt_service
from src.sc_chat.schemas.user import UserResponse
from src.sc_chat.repository.user_repository import UserRepository
from src.sc_chat.database.conn import get_db

router = APIRouter(prefix="/user", tags=["User"])


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Dependency to get user repository instance."""
    return UserRepository(db)


@router.get("/", response_model=list[UserResponse])
def get_users(user_repo: UserRepository = Depends(get_user_repository)):
    """Get all users."""
    users = user_repo.get_users()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repository),
    _=Depends(jwt_service.get_current_user),
):
    """Get a user by ID."""
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    return user
