from functools import lru_cache

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    vespera_version: str = "dev"
    log_level: str = "INFO"
    database_url: SecretStr
    check_interval: int = 10
    webhook_url: str
    redis_url: str
    shard_count: int = 1
    fault_error_rate: float = Field(default=0.0, ge=0.0, le=1.0)

@lru_cache
def get_settings() -> Settings:
    return Settings()