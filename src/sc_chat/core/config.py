from pydantic.v1 import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field("EduRag", env="APP_NAME")
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(True, env="DEBUG")

    database_url: str = Field(..., env="DATABASE_URL")
    async_database_url: str = Field(..., env="ASYNC_DATABASE_URL")

    secret_key: str = Field(..., env="SECRET_KEY")

    class Config:  # type: ignore
        """Configuration for Pydantic settings."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()  # type: ignore
