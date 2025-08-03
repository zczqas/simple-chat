from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from src.sc_chat.utils.common.enum import UserRoleEnum


class UserBase(BaseModel):
    """Base user schema with common fields."""

    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    is_active: bool
    role: UserRoleEnum
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserSignup(UserBase):
    """Schema for user signup."""

    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str
