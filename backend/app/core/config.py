from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(alias="APP_NAME")
    app_env: str = Field(alias="APP_ENV")
    api_v1_prefix: str = Field(alias="API_V1_PREFIX")
    database_url: str = Field(alias="DATABASE_URL")
    db_pool_size: int = Field(alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(alias="DB_POOL_TIMEOUT")
    dashboard_low_stock_threshold: int = Field(default=5, ge=0, alias="DASHBOARD_LOW_STOCK_THRESHOLD")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
