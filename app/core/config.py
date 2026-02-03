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
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"
    
    # Database - optional with fallback for Railway deployment
    DATABASE_URL: Optional[str] = None
    
    # Redis - optional with fallback
    REDIS_URL: Optional[str] = None
    
    # TikTok API Configuration - all optional for startup
    TIKTOK_CLIENT_KEY: Optional[str] = None
    TIKTOK_CLIENT_SECRET: Optional[str] = None
    TIKTOK_ACCESS_TOKEN: Optional[str] = None
    TIKTOK_WEBHOOK_SECRET: Optional[str] = None
    TIKTOK_BUSINESS_ID: Optional[str] = None
    TIKTOK_MESSAGING_API_BASE_URL: str = "https://business-api.tiktok.com/open_api/v1.3"
    
    # OpenAI - optional
    OPENAI_API_KEY: Optional[str] = None
    
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
    
    @property
    def is_configured(self) -> bool:
        """Check if all required API credentials are configured."""
        return all([
            self.DATABASE_URL,
            self.REDIS_URL,
            self.TIKTOK_CLIENT_KEY,
            self.TIKTOK_CLIENT_SECRET,
            self.TIKTOK_ACCESS_TOKEN,
            self.TIKTOK_WEBHOOK_SECRET,
            self.TIKTOK_BUSINESS_ID,
            self.OPENAI_API_KEY,
        ])
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        """Ensure DATABASE_URL uses async driver if provided.
        
        Automatically converts standard postgresql:// URLs to postgresql+asyncpg://
        for Railway and other providers that don't include the driver prefix.
        """
        if not v:
            return v
        
        # If already has asyncpg driver, return as-is
        if v.startswith("postgresql+asyncpg://"):
            return v
        
        # Convert standard postgresql:// to asyncpg driver
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Raise error for other protocols
        raise ValueError(
            "DATABASE_URL must be a PostgreSQL URL (postgresql:// or postgresql+asyncpg://)"
        )
    
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
