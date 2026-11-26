"""Application settings loaded from environment variables and .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurable application values shared by all application modules."""

    app_name: str = "Address Book API"
    app_version: str = "1.0.0"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    database_url: str = "sqlite:///./address_book.db"
    log_level: str = "INFO"
    log_dir: str = "logs"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
