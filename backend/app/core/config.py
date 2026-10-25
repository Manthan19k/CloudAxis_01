"""Centralised configuration loaded from environment variables."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Union

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_FILE = os.path.join(BACKEND_DIR, "cloudaxis.db").replace("\\", "/")
DEFAULT_SQLITE_URL = f"sqlite+aiosqlite:///{DEFAULT_DB_FILE}"


class Settings(BaseSettings):
    """Application settings sourced from the environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=os.path.join(BACKEND_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application -------------------------------------------------------
    PROJECT_NAME: str = "CloudAxis Enterprise Infrastructure Intelligence Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    app_name: str = "CloudAxis Enterprise Infrastructure Intelligence Platform"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="APP_DEBUG")

    # --- Database ----------------------------------------------------------
    database_url: str = Field(
        default=DEFAULT_SQLITE_URL,
        alias="DATABASE_URL",
    )
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    db_pool_recycle: int = Field(default=3600, alias="DB_POOL_RECYCLE")

    @field_validator("database_url", mode="after")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if not v:
            return DEFAULT_SQLITE_URL
        # If relative sqlite URL or pointing to cloudaxis.db, ensure it points to backend/cloudaxis.db
        if "sqlite" in v and ("./cloudaxis.db" in v or v.endswith("/cloudaxis.db") or v.endswith("\\cloudaxis.db")):
            return DEFAULT_SQLITE_URL
        return v

    # --- Security ----------------------------------------------------------
    secret_key: str = Field(default="super-secret-key-change-me-in-production", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

    # --- CORS --------------------------------------------------------------
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
        alias="BACKEND_CORS_ORIGINS",
    )
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
        alias="ALLOWED_ORIGINS",
    )

    # --- Frontend ----------------------------------------------------------
    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")

    # --- Rate limiting -----------------------------------------------------
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=120, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, alias="RATE_LIMIT_WINDOW_SECONDS")

    # --- Demo / seeding ----------------------------------------------------
    seed_on_startup: bool = Field(default=False, alias="SEED_ON_STARTUP")

    @property
    def allowed_origins_list(self) -> List[str]:
        origins = self.BACKEND_CORS_ORIGINS or self.allowed_origins
        if isinstance(origins, str):
            return [o.strip() for o in origins.split(",") if o.strip()]
        return list(origins)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

