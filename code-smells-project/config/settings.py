"""Configuration layer — the single owner of settings, loaded from the environment.

No secret is hardcoded: ``SECRET_KEY`` comes from the environment and, when absent,
an ephemeral random key is generated (with a warning) so the app can still boot in
development without committing a secret.
"""

import logging
import os
import secrets


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    def __init__(self) -> None:
        self.SECRET_KEY = os.environ.get("SECRET_KEY")
        if not self.SECRET_KEY:
            self.SECRET_KEY = secrets.token_hex(32)
            logging.getLogger("config").warning(
                "SECRET_KEY not set in environment; generated an ephemeral key. "
                "Set SECRET_KEY for stable sessions/tokens."
            )

        self.DEBUG = _as_bool(os.environ.get("DEBUG"), default=False)
        self.DB_PATH = os.environ.get("DB_PATH", "loja.db")
        self.HOST = os.environ.get("HOST", "0.0.0.0")
        self.PORT = int(os.environ.get("PORT", "5000"))
        self.TOKEN_MAX_AGE = int(os.environ.get("TOKEN_MAX_AGE", "3600"))
        # Explicit CORS origins instead of an open wildcard default.
        origins = os.environ.get("CORS_ORIGINS", "http://localhost:5000")
        self.CORS_ORIGINS = [o.strip() for o in origins.split(",") if o.strip()]


settings = Settings()
