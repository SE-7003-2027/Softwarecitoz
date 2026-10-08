import json
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    JWT_ACTIVE_KID: str
    JWT_PRIVATE_KEY_PEM: str
    JWT_PUBLIC_KEYS_JSON: str

    ACCESS_TTL: int = 15 * 60
    REFRESH_IDLE_TTL: int = 7 * 24 * 3600
    SESSION_ABSOLUTE_TTL: int = 30 * 24 * 3600
    REFRESH_REUSE_GRACE: int = 20
    OPENID_STATE_TTL: int = 10 * 60
    CLOCK_LEEWAY: int = 30

    @property
    def public_keys(self) -> dict[str, str]:
        return json.loads(self.JWT_PUBLIC_KEYS_JSON)


@lru_cache
def get_auth_settings() -> AuthConfig:
    return AuthConfig()
