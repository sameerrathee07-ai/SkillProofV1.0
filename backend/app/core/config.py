from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    GATE_THRESHOLD: float = 6.0
    TOKENS_PER_ACCEPTED_ANSWER: int = 2
    SIGNUP_TOKENS: int = 20
    DATABASE_URL: str = "sqlite:///./skillproof.db"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()