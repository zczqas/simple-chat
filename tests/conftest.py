from src.sc_chat.core.config import settings

settings.environment = "testing"
settings.debug = False
settings.database_url = "postgresql+asyncpg://user:password@localhost:5432/test_db"
