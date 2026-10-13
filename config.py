# config.py

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated application configuration."""

    app_name: str = "Financial Analysis Platform"

    environment: Literal[
        "development",
        "testing",
        "production",
    ] = "development"

    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    api_timeout_seconds: float = Field(
        default=10.0,
        gt=0,
        le=120.0,
    )

    financial_data_api_key: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("app_name")
    @classmethod
    def validate_app_name(cls, value: str) -> str:
        """Reject empty application names."""

        value = value.strip()

        if not value:
            raise ValueError(
                "Application name cannot be empty."
            )

        return value

    @field_validator("financial_data_api_key")
    @classmethod
    def validate_api_key(
        cls,
        value: SecretStr | None,
    ) -> SecretStr | None:
        """Reject an explicitly supplied empty API key."""

        if value is not None and not value.get_secret_value().strip():
            raise ValueError(
                "Financial data API key cannot be empty."
            )

        return value

    def validate_runtime_requirements(self) -> None:
        """Validate settings required by the active application."""

        if (
            self.environment == "production"
            and self.financial_data_api_key is None
        ):
            raise ValueError(
                "FINANCIAL_DATA_API_KEY is required "
                "in production."
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached, validated settings instance."""

    settings = Settings()
    settings.validate_runtime_requirements()

    return settings


settings = get_settings()
