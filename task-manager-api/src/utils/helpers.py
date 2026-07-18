"""Small pure helpers reused across services (single source of truth)."""
import re

EMAIL_RE = re.compile(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")


def calculate_percentage(part, total):
    if not total:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email) -> bool:
    return bool(email and EMAIL_RE.match(email))
