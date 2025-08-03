from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from src.sc_chat.database.conn import get_db
from src.sc_chat.models.user import User
from src.sc_chat.repository.auth_repository import AuthRepository
from src.sc_chat.schemas.user import RefreshTokenRequest, UserSignup
from src.sc_chat.security.auth import jwt_service

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_repository(db: Session = Depends(get_db)) -> AuthRepository:
    """Dependency to get auth repository instance."""
    return AuthRepository(db)


@router.post("/login")
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """
    Login endpoint that authenticates user and returns access and refresh tokens.
    """
    user = auth_repo.authenticate_user(
        email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=jwt_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt_service.create_access_token(
        data={"email": user.email, "role": user.role.value},
        expires_delta=access_token_expires,
    )

    refresh_token_expires = timedelta(minutes=jwt_service.REFRESH_TOKEN_TIME_IN_MINUTES)
    refresh_token = jwt_service.create_refresh_token(
        data={"email": user.email, "role": user.role.value},
        expires_delta=refresh_token_expires,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
        },
    }


@router.post("/signup", response_model=dict)
def signup_user(
    user_data: UserSignup, auth_repo: AuthRepository = Depends(get_auth_repository)
):
    """
    Signup endpoint that creates a new user account.
    """
    if auth_repo.user_exists_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    if auth_repo.user_exists_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )

    try:
        new_user = auth_repo.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
        )

        return {
            "message": f"User {user_data.email} signed up successfully",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "username": new_user.username,
                "role": new_user.role,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user account{str(e)}",
        ) from e


@router.post("/refresh")
def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """
    Refresh token endpoint that generates new access token using refresh token.
    """
    try:
        email = jwt_service.decode_access_token_and_return_email(
            refresh_data.refresh_token
        )
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = auth_repo.get_user_by_email(email)
        if not user or user.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(
            minutes=jwt_service.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = jwt_service.create_access_token(
            data={"email": user.email, "role": user.role.value},
            expires_delta=access_token_expires,
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.get("/me")
def get_current_user_info(current_user: User = Depends(jwt_service.get_current_user)):
    """
    Get current authenticated user information.
    """
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at,
        }
    }
