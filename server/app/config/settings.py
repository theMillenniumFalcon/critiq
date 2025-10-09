"""
Application configuration using pydantic BaseSettings.
Supports environment-specific configuration files.
"""
import os
from functools import lru_cache
from typing import Optional
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

    # Celery Configuration
    celery_broker_url: str = Field(default="redis://localhost:6379/1", description="Celery broker URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", description="Celery result backend URL")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # AI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")

    # Vector Storage Configuration
    embedding_model: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")
    vector_dimension: int = Field(default=1536, env="VECTOR_DIMENSION")
    similarity_threshold: float = Field(default=0.85, env="SIMILARITY_THRESHOLD")
    
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
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
    """Get cached settings instance with environment-specific config."""
    env = os.getenv('ENV', 'development')
    env_file = f".env.{env}"
    
    # Check if environment-specific file exists, fallback to .env
    if os.path.exists(env_file):
        return Settings(_env_file=env_file)
    return Settings(_env_file='.env')


# Create global settings instance
settings = get_settings()