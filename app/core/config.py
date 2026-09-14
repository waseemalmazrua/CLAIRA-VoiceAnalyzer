from functools import cache

from pydantic import Field, HttpUrl, PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: PostgresDsn = Field(alias="DATABASE_URL")
    redis_url: RedisDsn

    openai_api_key: SecretStr
    groq_api_key: SecretStr
    runpod_api_key: SecretStr

    allow_origins: HttpUrl


 

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False,
    )

@cache
def get_settings():
    return Settings()

settings = get_settings()
