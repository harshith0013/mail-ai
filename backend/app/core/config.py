import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is missing."
        )

    return value


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./mail_ai.db",
)

GOOGLE_CLIENT_ID = get_required_env(
    "GOOGLE_CLIENT_ID"
)

GOOGLE_CLIENT_SECRET = get_required_env(
    "GOOGLE_CLIENT_SECRET"
)

GOOGLE_REDIRECT_URI = get_required_env(
    "GOOGLE_REDIRECT_URI"
)

GOOGLE_PROJECT_ID = os.getenv(
    "GOOGLE_PROJECT_ID"
)

GEMINI_API_KEY = get_required_env(
    "GEMINI_API_KEY"
)

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development",
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5174",
)