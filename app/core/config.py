import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""
    # PostgreSQL settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/knowledge_base"
    )
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
