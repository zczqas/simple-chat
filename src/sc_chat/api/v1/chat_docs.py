from fastapi import APIRouter, Depends
from typing import Dict, Any

from src.sc_chat.security.rbac import require_user
from src.sc_chat.models.user import User

router = APIRouter(prefix="/chat", tags=["Chat Documentation"])


@router.get("/websocket-info", response_model=Dict[str, Any])
def get_websocket_info(current_user: User = Depends(require_user())):
    """
    Get WebSocket connection information and API documentation.
    """
    return {
        "websocket_endpoint": "/ws/{room_id}",
        "authentication": {
            "method": "JWT Token",
            "query_parameter": "?token=your_jwt_token",
            "header": "Authorization: Bearer your_jwt_token",
        },
        "connection_example": {
            "javascript": "new WebSocket('ws://localhost:8000/ws/1?token=your_jwt_token')",
            "python": "import websockets; websockets.connect('ws://localhost:8000/ws/1?token=your_jwt_token')",
        },
        "message_formats": {
            "send_message": {"type": "message", "content": "Hello, world!"},
            "fetch_history": {"type": "fetch_messages", "cursor": 123, "limit": 50},
        },
        "response_formats": {
            "new_message": {
                "type": "message",
                "data": {
                    "id": 1,
                    "content": "Hello, world!",
                    "user_id": 1,
                    "username": "john_doe",
                    "room_id": 1,
                    "created_at": "2025-08-04T10:30:00",
                },
            },
            "message_history": {
                "type": "messages_history",
                "data": {
                    "messages": "Array of message objects",
                    "has_more": True,
                    "next_cursor": 100,
                },
            },
            "error": {"type": "error", "message": "Error description"},
        },
        "room_info": {
            "description": "Replace {room_id} with the actual room ID you want to join",
            "example": "/ws/1 for room with ID 1",
        },
    }
