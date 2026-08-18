from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BookOps AI"
    environment: str = "development"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./bookops.db"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 480
    frontend_origins: str = "http://localhost:5173,http://localhost:8080"

    admin_email: str = "owner@bookops.local"
    admin_password: str = "ChangeMe123!"
    business_name: str = "BookOps Demo Salon"
    business_timezone: str = "Asia/Jerusalem"

    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    notification_email: str | None = None

    reminder_minutes: int = 60
    daily_summary_hour: int = 19

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
