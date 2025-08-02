from fastapi import FastAPI

from src.sc_chat.core.config import settings
from src.sc_chat.urls import InitializeRouter

# from fastapi.staticfiles import StaticFiles


app = FastAPI(title=settings.app_name, debug=settings.debug)

# Mount the static directory
# app.mount("/static", StaticFiles(directory="src/sc_chat/static"), name="static")

InitializeRouter(app).initialize_router()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Simple Chat App!"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "debug": settings.debug,
    }
