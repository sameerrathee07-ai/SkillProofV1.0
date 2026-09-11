"""Application configuration via Pydantic Settings."""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All environment variables, validated and typed."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---- Required: Application ----
    SECRET_KEY: str = Field(..., description="JWT signing secret (32+ chars)")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=1440, description="Access token lifetime in minutes"
    )
    ENVIRONMENT: str = Field(
        default="development", description="development | staging | production"
    )

    # ---- Required: Database ----
    DATABASE_URL: str = Field(
        default="sqlite:///./pitchpal.db", description="SQLAlchemy database URL"
    )
    POSTGRES_PASSWORD: str = Field(
        default="", description="PostgreSQL password for docker-compose"
    )

    # ---- Required: CORS ----
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Comma-separated allowed origins",
    )

    # ---- Optional: Google OAuth ----
    GOOGLE_CLIENT_ID: str = Field(
        default="", description="Google OAuth Web Client ID"
    )

    # ---- Optional: Razorpay (Payments) ----
    RAZORPAY_KEY_ID: str = Field(
        default="rzp_test_placeholder", description="Razorpay Key ID"
    )
    RAZORPAY_KEY_SECRET: str = Field(
        default="rzp_test_placeholder", description="Razorpay Key Secret"
    )

    # ---- Optional: Error Tracking ----
    SENTRY_DSN: str = Field(
        default="", description="Sentry DSN for error tracking"
    )

    # ---- Optional: Feature Flags ----
    ALLOW_UNVERIFIED_PURCHASE: bool = Field(
        default=False, description="Allow token purchases without payment verification"
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()