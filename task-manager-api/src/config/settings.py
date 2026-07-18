"""Centralized, environment-driven configuration.

SECRET_KEY, DB URI and the SMTP credentials (which used to be hardcoded in
app.py and notification_service.py) are all sourced from environment variables.
Domain constants that were scattered magic values also live here.
"""
import os


def _get_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    # --- Security / runtime ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me-in-prod")
    DEBUG = _get_bool("FLASK_DEBUG", False)
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

    # --- Database ---
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- CORS (allowlist instead of wide-open "*") ---
    CORS_ORIGINS = [
        o.strip()
        for o in os.environ.get(
            "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
        ).split(",")
        if o.strip()
    ]

    # --- SMTP (was hardcoded in notification_service.py) ---
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

    # --- Domain constants (were magic numbers / duplicated literal lists) ---
    VALID_STATUSES = ["pending", "in_progress", "done", "cancelled"]
    VALID_ROLES = ["user", "admin", "manager"]
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 200
    MIN_PASSWORD_LENGTH = 4
    MIN_PRIORITY = 1
    MAX_PRIORITY = 5
    DEFAULT_PRIORITY = 3


settings = Settings()
