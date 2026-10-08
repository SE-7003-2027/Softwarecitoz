from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ITADConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ITAD_API_KEY: str


@lru_cache
def get_itad_settings() -> ITADConfig:
    return ITADConfig()
