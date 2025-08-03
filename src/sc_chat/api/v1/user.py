from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.sc_chat.repository.user_repository import UserRepository
from src.sc_chat.database.conn import get_db

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/")
def get_users(db: Session = Depends(get_db)):
    """Get all users."""
    users = UserRepository(db).get_users()
    return {"users": users}


@router.get("/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Get a user by ID."""
    user = UserRepository(db).get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    return {"user": user}
