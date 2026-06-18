"""Application settings, loaded from environment / .env via pydantic-settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Database — async driver URL (sqlite+aiosqlite dev / postgresql+asyncpg prod)
    database_url: str = "sqlite+aiosqlite:///./upstream.db"

    # Auth (JWT in httpOnly cookies — see plan.md §6.0)
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    refresh_token_days: int = 7

    # Cookie settings. For same-site dev use samesite=lax + secure=false;
    # for the split-origin Vercel↔Railway prod use samesite=none + secure=true.
    cookie_domain: str | None = None
    cookie_secure: bool = False
    cookie_samesite: str = "lax"  # "lax" | "strict" | "none"
    access_cookie_name: str = "up_access"
    refresh_cookie_name: str = "up_refresh"

    # CORS — comma-separated origins (explicit; never "*" with credentials)
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def sync_database_url(self) -> str:
        """Sync driver URL for Alembic migrations (the app engine stays async)."""
        return self.database_url.replace("+aiosqlite", "").replace("+asyncpg", "+psycopg2")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
