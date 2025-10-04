"""Application configuration using pydantic BaseSettings."""

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")

    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
