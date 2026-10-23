# bento_services/ner_config.py

from functools import cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class NERSettings(BaseSettings):
    hf_token: SecretStr
    logfire_token: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
        env_file_encoding="utf-8",
    )


@cache
def get_ner_settings():
    return NERSettings()


ner_settings = get_ner_settings()
