"""Centralized, environment-driven configuration.

Every secret and tunable lives here and is sourced from environment variables
with safe defaults. Nothing sensitive is hardcoded (fixes: Hardcoded Secrets,
Debug-in-Prod, Magic Numbers).
"""
import os


def _get_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    # --- Security / runtime ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me-in-prod")
    DEBUG = _get_bool("FLASK_DEBUG", False)  # off by default; never debug in prod
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

    # --- Database ---
    DB_PATH = os.environ.get("DB_PATH", "loja.db")

    # --- CORS (allowlist instead of wide-open "*") ---
    CORS_ORIGINS = [
        o.strip()
        for o in os.environ.get(
            "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
        ).split(",")
        if o.strip()
    ]

    # --- Admin operations token (empty => destructive admin ops disabled) ---
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

    # --- Business constants (were magic numbers scattered in the code) ---
    # (faturamento threshold, discount rate)
    DISCOUNT_TIERS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]
    CATEGORIAS_VALIDAS = [
        "informatica",
        "moveis",
        "vestuario",
        "geral",
        "eletronicos",
        "livros",
    ]
    STATUS_PEDIDO_VALIDOS = [
        "pendente",
        "aprovado",
        "enviado",
        "entregue",
        "cancelado",
    ]
    NOME_MIN = 2
    NOME_MAX = 200


settings = Settings()
