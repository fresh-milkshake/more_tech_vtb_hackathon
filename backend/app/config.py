from pydantic_settings import BaseSettings
from typing import List
import os
from urllib.parse import quote_plus


class Settings(BaseSettings):
    """
    Application settings configuration using Pydantic BaseSettings.
    
    Manages all configuration parameters for the HR Avatar Backend including
    database connections, external service API keys, audio processing settings,
    and file storage paths.
    """
    # Application settings
    APP_NAME: str = "HR Avatar Backend"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080"
    
    # External service API keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY")
    
    # Audio processing configuration
    MAX_AUDIO_DURATION: int = 300  # Maximum audio duration in seconds
    AUDIO_SAMPLE_RATE: int = 16000  # Audio sample rate for processing
    RESPONSE_TIMEOUT: int = 60  # Response timeout in seconds
    
    # File storage paths
    UPLOAD_DIR: str = "uploads"
    STATIC_DIR: str = "static"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra environment variables

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated ALLOWED_ORIGINS string to a list of cleaned origin URLs."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    @property
    def safe_database_url(self) -> str:
        """
        Get database URL with properly escaped password for PostgreSQL connections.
        
        Handles URL encoding of special characters in database passwords to ensure
        proper connection string formatting.
        """
        if self.DATABASE_URL.startswith("postgresql://"):
            parts = self.DATABASE_URL.split("://")
            if len(parts) == 2:
                protocol = parts[0]
                rest = parts[1]
                if "@" in rest:
                    user_pass, host_db = rest.split("@", 1)
                    if ":" in user_pass:
                        user, password = user_pass.split(":", 1)
                        escaped_password = quote_plus(password)
                        return f"{protocol}://{user}:{escaped_password}@{host_db}"
        return self.DATABASE_URL


settings = Settings()


def ensure_directories_exist():
    """Create required directories if they don't exist."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.STATIC_DIR, exist_ok=True)

ensure_directories_exist()