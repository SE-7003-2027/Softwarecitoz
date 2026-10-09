from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la API leída de variables de entorno y `.env`."""

    app_name: str = "Chaos API"
    app_env: Literal["dev", "prod"] = "dev"
    log_level: str = "info"
    allowed_origins: list[str] = ["http://localhost:3000"]

    steam_api_key: SecretStr
    steam_api_base_url: str = "https://api.steampowered.com"
    steam_timeout_seconds: float = 10.0

    BASE_URL: str = "http://localhost:8000"
    DATABASE_URL: str
    COOKIE_SECURE: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Regresa la instancia única de Settings (se cachea)."""
    return Settings()
