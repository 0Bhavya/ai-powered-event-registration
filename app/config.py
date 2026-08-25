"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central application settings."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "AI Event Registration"
    app_url: str = "http://localhost:8000"
    debug: bool = True
    demo_mode: bool = True
    demo_payment_mode: bool = True

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_secret: str = "dev-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Database
    database_url: str = "postgresql://postgres:postgres@127.0.0.1:5433/event_registration"

    # Razorpay
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""

    # Email / SMTP Settings
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = "noreply@eventai.com"

    @property
    def templates_dir(self) -> Path:
        return BASE_DIR / "templates"

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "static"


@lru_cache
def get_settings() -> Settings:
    return Settings()
