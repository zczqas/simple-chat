from typing import Optional
from fastapi import WebSocket, status
from jose import JWTError
from sqlalchemy.orm import Session

from src.sc_chat.security.auth import jwt_service
from src.sc_chat.database.conn import get_db
from src.sc_chat.models.user import User


async def authenticate_websocket(websocket: WebSocket, token: str) -> Optional[User]:
    """
    Authenticate WebSocket connection using JWT token.

    Args:
        websocket: The WebSocket connection
        token: JWT token from query parameter or header

    Returns:
        User object if authentication successful, None otherwise
    """
    try:
        email = jwt_service.decode_access_token_and_return_email(token)
        if not email:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token"
            )
            return None

        db: Session = next(get_db())

        try:
            user = jwt_service.get_user(email=email, db=db)
            if not user:
                await websocket.close(
                    code=status.WS_1008_POLICY_VIOLATION, reason="User not found"
                )
                return None

            if user.is_active is False:
                await websocket.close(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="User account is deactivated",
                )
                return None

            return user

        finally:
            db.close()

    except JWTError:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token"
        )
        return None
    except Exception as e:
        print(f"WebSocket authentication error: {e}")
        await websocket.close(
            code=status.WS_1011_INTERNAL_ERROR, reason="Authentication error"
        )
        return None


def extract_token_from_websocket(websocket: WebSocket) -> Optional[str]:
    """
    Extract JWT token from WebSocket connection.
    Checks query parameters first, then headers.

    Args:
        websocket: The WebSocket connection

    Returns:
        JWT token if found, None otherwise
    """
    token = websocket.query_params.get("token")
    if token:
        return token

    auth_header = websocket.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    return None
