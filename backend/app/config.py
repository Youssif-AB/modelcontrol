from functools import lru_cache
from typing import Literal

from pydantic import (
    SecretStr,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    environment: Literal[
        "development",
        "test",
        "production",
    ] = "development"

    database_url: str
    jwt_secret_key: SecretStr

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 60

    cors_origins: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    )

    allowed_hosts: str = (
        "localhost,"
        "127.0.0.1,"
        "testserver"
    )

    docs_enabled: bool = True
    log_level: str = "INFO"

    rate_limit_enabled: bool = True

    mlflow_tracking_uri: str = (
        "http://localhost:5000"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(
        self,
    ) -> list[str]:
        return [
            value.strip()
            for value
            in self.cors_origins.split(",")
            if value.strip()
        ]

    @property
    def allowed_host_list(
        self,
    ) -> list[str]:
        return [
            value.strip()
            for value
            in self.allowed_hosts.split(",")
            if value.strip()
        ]

    @model_validator(mode="after")
    def validate_production_settings(
        self,
    ):
        if self.environment != "production":
            return self

        secret = (
            self.jwt_secret_key
            .get_secret_value()
        )

        if len(secret) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least "
                "32 characters in production"
            )

        if "*" in self.cors_origin_list:
            raise ValueError(
                "Wildcard CORS origins are not "
                "allowed in production"
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()