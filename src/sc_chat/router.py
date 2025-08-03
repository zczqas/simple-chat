from src.sc_chat.api.v1.user import router as user_router
from src.sc_chat.api.v1.auth import router as auth_router

routers = {
    "User": user_router,
    "Auth": auth_router,
}
