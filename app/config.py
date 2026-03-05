import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, BaseSettings, Field, ValidationError


load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


class Settings(BaseSettings):
    APP_NAME: str = Field("MCP GraphQL Server", env="APP_NAME")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    PORT: int = Field(8000, env="PORT")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    DATABASE_URL: AnyHttpUrl = Field(..., env="DATABASE_URL")

    class Config:
        case_sensitive = True


def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        raise RuntimeError(
            f"Configuration validation error: {exc.errors()}"
        ) from exc