"""Application configuration management using Pydantic."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./tracecredit.db")
    
    # Model
    model_dir: str = "models"
    active_model_version: str = "v1"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/tracecredit.log"
    
    # Features
    feature_engineering_enabled: bool = True
    baseline_month: int = 1
    
    # Drift Detection
    drift_threshold_percentage: float = 20.0
    drift_sensitivity: float = 0.05
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = "allow"

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"

    def get_log_file_path(self) -> Path:
        """Get full path to log file."""
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path


# Global settings instance
settings = Settings()
