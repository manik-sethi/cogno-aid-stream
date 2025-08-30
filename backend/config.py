import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # App settings
    app_name: str = "BCI Confusion Monitor API"
    version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Database settings
    database_url: str = Field(
        default="sqlite+aiosqlite:///./bci_monitor.db",
        env="DATABASE_URL"
    )
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:8080", "http://localhost:3000"],
        env="CORS_ORIGINS"
    )
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # BCI Device settings
    emotiv_client_id: Optional[str] = Field(default=None, env="EMOTIV_CLIENT_ID")
    emotiv_client_secret: Optional[str] = Field(default=None, env="EMOTIV_CLIENT_SECRET")
    mock_bci_mode: bool = Field(default=True, env="MOCK_BCI_MODE")
    
    # Confusion detection settings
    default_confusion_threshold: float = Field(default=0.7, env="CONFUSION_THRESHOLD")
    confusion_window_size: int = Field(default=50, env="CONFUSION_WINDOW_SIZE")
    signal_sampling_rate: int = Field(default=128, env="SAMPLING_RATE")
    
    # AI/LLM settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-vision-preview", env="OPENAI_MODEL")
    openai_text_model: str = Field(default="gpt-4", env="OPENAI_TEXT_MODEL")
    openai_max_tokens: int = Field(default=500, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    mock_llm_mode: bool = Field(default=True, env="MOCK_LLM_MODE")
    
    # Screenshot settings
    screenshot_dir: str = Field(default="./screenshots", env="SCREENSHOT_DIR")
    max_screenshot_history: int = Field(default=10, env="MAX_SCREENSHOT_HISTORY")
    screenshot_quality: int = Field(default=85, env="SCREENSHOT_QUALITY")
    
    # WebSocket settings
    websocket_heartbeat_interval: int = Field(default=30, env="WS_HEARTBEAT_INTERVAL")
    websocket_timeout: int = Field(default=300, env="WS_TIMEOUT")
    max_connections: int = Field(default=100, env="MAX_CONNECTIONS")
    
    # Data processing settings
    signal_highpass_freq: float = Field(default=1.0, env="SIGNAL_HIGHPASS_FREQ")
    signal_lowpass_freq: float = Field(default=50.0, env="SIGNAL_LOWPASS_FREQ")
    signal_notch_freq: float = Field(default=60.0, env="SIGNAL_NOTCH_FREQ")
    artifact_amplitude_threshold: float = Field(default=200.0, env="ARTIFACT_THRESHOLD")
    
    # Learning analytics settings
    analytics_enabled: bool = Field(default=True, env="ANALYTICS_ENABLED")
    data_retention_days: int = Field(default=30, env="DATA_RETENTION_DAYS")
    
    # Security settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(default=60, env="ACCESS_TOKEN_EXPIRE")
    
    # Monitoring settings
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # File paths
    data_dir: str = Field(default="./data", env="DATA_DIR")
    logs_dir: str = Field(default="./logs", env="LOGS_DIR")
    temp_dir: str = Field(default="./temp", env="TEMP_DIR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.screenshot_dir,
            self.data_dir,
            self.logs_dir,
            self.temp_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug or self.reload
    
    @property
    def database_echo(self) -> bool:
        """Enable SQLAlchemy query logging in development."""
        return self.is_development
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins

# Global settings instance
settings = Settings()

# Environment-specific configurations
def get_settings() -> Settings:
    """Get application settings."""
    return settings

def configure_logging():
    """Configure application logging."""
    import logging.config
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.log_level,
                "formatter": "detailed",
                "filename": f"{settings.logs_dir}/bci_monitor.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": settings.log_level,
                "handlers": ["console", "file"],
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "INFO" if settings.database_echo else "WARNING",
                "handlers": ["file"],
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(logging_config)