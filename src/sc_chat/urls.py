from fastapi import FastAPI

from src.sc_chat.router import routers


class InitializeRouter:
    def __init__(self, app: FastAPI):
        self.app = app

    def initialize_router(self):
        for prefix, router in routers.items():
            self.app.include_router(router=router, prefix="/api/v1", tags=[prefix])
