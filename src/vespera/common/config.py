from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    vespera_version: str = "dev"
    log_level: str = "INFO"
    database_url: SecretStr
    http_port: int = 8000

@lru_cache
def get_settings() -> Settings:
    return Settings()