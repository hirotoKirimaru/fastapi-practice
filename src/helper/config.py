from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    ENV: Literal["local", "prod"]
    SECRET: str
    GOOGLE_API_KEY: str


settings = Settings()  # type: ignore
