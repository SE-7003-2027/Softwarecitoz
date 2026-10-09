from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class IGDBConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    TWITCH_CLIENT_ID: str
    TWITCH_CLIENT_SECRET: str


@lru_cache
def get_igdb_settings() -> IGDBConfig:
    return IGDBConfig()
