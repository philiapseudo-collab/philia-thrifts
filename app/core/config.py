"""
Core configuration module using pydantic-settings.
Loads environment variables with strict type validation.
"""
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable loading."""
    
    # Environment
    ENVIRONMENT: str = "local"
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # TikTok API Configuration
    TIKTOK_CLIENT_KEY: str
    TIKTOK_CLIENT_SECRET: str
    TIKTOK_ACCESS_TOKEN: str
    TIKTOK_WEBHOOK_SECRET: str
    TIKTOK_BUSINESS_ID: str  # Required in message send payload
    TIKTOK_MESSAGING_API_BASE_URL: str = "https://business-api.tiktok.com/open_api/v1.3"
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    
    # Monitoring (Optional)
    SENTRY_DSN: Optional[str] = None
    
    # Computed Properties
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_local(self) -> bool:
        """Check if running in local development environment."""
        return self.ENVIRONMENT.lower() == "local"
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure DATABASE_URL uses async driver."""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use asyncpg driver: postgresql+asyncpg://..."
            )
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is acceptable."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra env vars
    )


# Global settings instance (singleton pattern)
settings = Settings()
