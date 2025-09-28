"""Common configuration settings for all microservices."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    """Common settings for all microservices."""

    model_config = SettingsConfigDict(
        env_file=".env",
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
    MONGODB_HOST: str = Field(default="localhost", description="MongoDB host")
    MONGODB_PORT: int = Field(default=27019, description="MongoDB port")
    MONGODB_USERNAME: str = Field(default="root", description="MongoDB username")
    MONGODB_PASSWORD: str = Field(default="example", description="MongoDB password")
    MONGODB_DATABASE_PREFIX: str = Field(default="q", description="Database prefix")
    MONGODB_AUTH_SOURCE: str = Field(default="admin", description="MongoDB auth source")

    # Security Settings
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production", description="Secret key for JWT"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")

    # API Settings
    API_PREFIX: str = Field(default="/api/v1", description="API prefix")
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
    def mongodb_url(self) -> str:
        """Get MongoDB connection URL."""
        if self.MONGODB_USERNAME and self.MONGODB_PASSWORD:
            return f"mongodb://{self.MONGODB_USERNAME}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/?authSource={self.MONGODB_AUTH_SOURCE}"
        return f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}/"

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

    def get_database_name(self, service_name: str) -> str:
        """Get database name for a service."""
        clean_service = service_name.replace("-", "_").replace(" ", "_").lower()
        return f"{self.MONGODB_DATABASE_PREFIX}_{clean_service}"


# Global settings instance
settings = CommonSettings()


def get_settings() -> CommonSettings:
    """Get the global settings instance."""
    return settings
