"""Common configuration settings for all microservices."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    """Common settings for all microservices."""

    model_config = SettingsConfigDict(
        env_file=["../.env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",  # Allow extra fields from .env
    )

    # Project Settings
    PROJECT_NAME: str = Field(default="Quant Platform", description="Project name")
    ENVIRONMENT: str = Field(
        default="development",
        description="Environment (development, staging, production)",
    )
    DEBUG: bool = Field(default=True, description="Debug mode")
    DEV_MODE: bool = Field(default=True, description="Development mode")
    MOCK_DATABASE: bool = Field(default=False, description="Use mock database")

    # Database Settings
    MONGODB_SERVER: str = Field(default="localhost:27019", description="MongoDB host")
    MONGODB_USERNAME: str = Field(default="root", description="MongoDB username")
    MONGODB_PASSWORD: str = Field(default="example", description="MongoDB password")

    ALPHA_VANTAGE_API_KEY: str = Field(
        default="demo", description="Alpha Vantage API Key"
    )

    # Security Settings
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production", description="Secret key for JWT"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")

    # API Settings
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS origins",
    )

    # Performance Settings
    MAX_CONNECTIONS_COUNT: int = Field(
        default=10, description="Max database connections"
    )
    MIN_CONNECTIONS_COUNT: int = Field(
        default=1, description="Min database connections"
    )

    @property
    def all_cors_origins(self) -> list[str]:
        """Get all CORS origins including environment-specific ones."""
        origins = self.CORS_ORIGINS.copy()

        # Add localhost variants for development
        if self.ENVIRONMENT in ["development", "local"]:
            dev_origins = [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://localhost:8080",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000",
                "http://127.0.0.1:8080",
            ]
            for origin in dev_origins:
                if origin not in origins:
                    origins.append(origin)

        return origins


# Global settings instance
settings = CommonSettings()


def get_settings() -> CommonSettings:
    """Get the global settings instance."""
    return settings
