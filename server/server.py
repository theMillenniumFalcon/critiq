"""
Critiq API Server Entry Point

Simplified server runner that uses environment-specific configuration.
Run with: python server.py
"""
import uvicorn
from app.config.settings import settings


def main():
    """Run the API server with configuration from settings."""
    print(f"🚀 Starting Critiq API")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🌐 Host: {settings.api_host}:{settings.api_port}")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,  # Auto-reload enabled in debug mode
        log_level="debug" if settings.debug else "info"
    )


if __name__ == "__main__":
    main()