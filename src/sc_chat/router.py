from src.sc_chat.api.v1.auth import router as auth_router
from src.sc_chat.api.v1.user import router as user_router
from src.sc_chat.api.v1.rooms import router as rooms_router
from src.sc_chat.api.v1.chat_docs import router as chat_docs_router
from src.sc_chat.websocket.chat import router as websocket_router

routers = {
    "User": user_router,
    "Auth": auth_router,
    "Chat Rooms": rooms_router,
    "Chat Documentation": chat_docs_router,
    "WebSocket": websocket_router,
}
