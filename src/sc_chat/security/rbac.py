from typing import Callable, List, Union

from fastapi import Depends, HTTPException
from starlette import status

from src.sc_chat.models.user import User
from src.sc_chat.security.auth import jwt_service
from src.sc_chat.utils.common.enum import UserRoleEnum
from src.sc_chat.utils.common.exception import CredentialsValidationException


class RBACHandler:
    """Role-Based Access Control handler with hierarchy support."""

    # Role hierarchies
    ROLE_HIERARCHY = {
        UserRoleEnum.ADMIN: [UserRoleEnum.ADMIN, UserRoleEnum.USER],
        UserRoleEnum.USER: [UserRoleEnum.USER],
    }

    @classmethod
    def user_has_permission(
        cls, user_role: UserRoleEnum, required_roles: List[UserRoleEnum]
    ) -> bool:
        """Check if user role has permission based on hierarchy."""
        allowed_roles = cls.ROLE_HIERARCHY.get(user_role, [])
        return any(role in allowed_roles for role in required_roles)


def require_roles(roles: Union[UserRoleEnum, List[UserRoleEnum]]):
    if isinstance(roles, UserRoleEnum):
        roles = [roles]

    def get_user_with_roles(
        current_user: User = Depends(jwt_service.get_current_user),
    ) -> User:
        if not current_user or not current_user.role:  # type: ignore
            raise CredentialsValidationException("Could not validate user credentials")

        if not RBACHandler.user_has_permission(current_user.role, roles):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[role.value for role in roles]}",
            )

        return current_user

    return get_user_with_roles


def require_admin() -> Callable:
    """Require admin role - for admin-only endpoints."""
    return require_roles(UserRoleEnum.ADMIN)


def require_user() -> Callable:
    """Require user role - for authenticated user endpoints (both USER and ADMIN can access)."""
    return require_roles(UserRoleEnum.USER)
