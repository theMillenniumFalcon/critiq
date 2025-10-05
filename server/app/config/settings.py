"""
Application configuration using pydantic BaseSettings.
Supports environment-specific configuration files.
"""
import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment Configuration
    env: str = Field(default="development", description="Environment (development, staging, production)")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    debug: bool = Field(default=True, description="Debug mode")
    
    # Database Configuration
    database_url: str = Field(..., description="Database connection URL")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    def __init__(self, **data):
        # Determine which env file to load based on ENV variable
        env = os.getenv('ENV', 'development')
        env_file = f".env.{env}"
        
        # Check if environment-specific file exists, fallback to .env
        if os.path.exists(env_file):
            self.__class__.model_config = SettingsConfigDict(
                env_file=env_file,
                env_file_encoding="utf-8",
                case_sensitive=False,
                extra="ignore",
            )
        
        super().__init__(**data)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.env == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Create global settings instance
settings = get_settings()