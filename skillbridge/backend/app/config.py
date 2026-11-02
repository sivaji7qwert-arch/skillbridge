"""
Application configuration, loaded from environment variables.
Copy .env.example to .env and adjust as needed.
"""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]


def resolve_data_path(env_value: str | None, default: str) -> str:
    raw_value = env_value or default
    candidate = Path(raw_value)
    if candidate.is_absolute():
        return str(candidate)

    for base in (BACKEND_ROOT, PROJECT_ROOT):
        resolved = (base / candidate).resolve()
        if resolved.exists() or str(candidate).startswith((".", "..")):
            return str(resolved)

    return str((PROJECT_ROOT / candidate).resolve())


class Settings:
    APP_NAME: str = "SkillBridge API"
    ENV: str = os.getenv("ENV", "development")

    # PostgreSQL — platform data (accounts, jobs, applications, resumes, DSA progress)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/skillbridge"
    )

    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # Path to processed labour-market analytics (CSV pipeline output)
    DATA_DIR: str = resolve_data_path(os.getenv("DATA_DIR"), str(PROJECT_ROOT / "data" / "processed"))
    RAW_DATA_DIR: str = resolve_data_path(os.getenv("RAW_DATA_DIR"), str(PROJECT_ROOT / "data" / "raw"))

    # File uploads (resumes, certificates)
    UPLOAD_DIR: str = resolve_data_path(os.getenv("UPLOAD_DIR"), str(PROJECT_ROOT / "data" / "uploads"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
