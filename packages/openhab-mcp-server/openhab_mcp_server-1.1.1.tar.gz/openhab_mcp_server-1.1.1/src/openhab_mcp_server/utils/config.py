"""Configuration management for openHAB MCP server."""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import logging


class Config(BaseModel):
    """Configuration management from environment variables."""
    
    openhab_url: str = Field(
        default="http://localhost:8080",
        description="openHAB server URL"
    )
    openhab_token: Optional[str] = Field(
        default=None,
        description="openHAB API token for authentication"
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    retry_attempts: int = Field(
        default=3,
        description="Number of retry attempts for failed requests"
    )
    retry_backoff_factor: float = Field(
        default=2.0,
        description="Exponential backoff factor for retries"
    )
    retry_max_delay: int = Field(
        default=60,
        description="Maximum delay between retries in seconds"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    @validator('openhab_url')
    def validate_url(cls, v: str) -> str:
        """Ensure URL doesn't end with slash."""
        return v.rstrip('/')
    
    @validator('timeout')
    def validate_timeout(cls, v: int) -> int:
        """Ensure timeout is positive."""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v
    
    @validator('retry_attempts')
    def validate_retry_attempts(cls, v: int) -> int:
        """Ensure retry attempts is non-negative."""
        if v < 0:
            raise ValueError("Retry attempts must be non-negative")
        return v
    
    @validator('retry_backoff_factor')
    def validate_retry_backoff_factor(cls, v: float) -> float:
        """Ensure backoff factor is positive."""
        if v <= 0:
            raise ValueError("Retry backoff factor must be positive")
        return v
    
    @validator('retry_max_delay')
    def validate_retry_max_delay(cls, v: int) -> int:
        """Ensure max delay is positive."""
        if v <= 0:
            raise ValueError("Retry max delay must be positive")
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @validator('openhab_token')
    def validate_token(cls, v: Optional[str]) -> Optional[str]:
        """Validate token format and warn if missing."""
        if v is None or not v.strip():
            logging.getLogger(__name__).warning(
                "No openHAB API token configured. Authentication may fail."
            )
            return None
        
        # Basic token format validation
        token = v.strip()
        if len(token) < 10:
            raise ValueError("API token appears to be too short")
        
        return token
    
    def __str__(self) -> str:
        """String representation with masked token."""
        token_display = "***" if self.openhab_token else "None"
        return (
            f"Config(url={self.openhab_url}, token={token_display}, "
            f"timeout={self.timeout}, log_level={self.log_level})"
        )
    
    def __repr__(self) -> str:
        """Representation with masked token."""
        return self.__str__()
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        return cls(
            openhab_url=os.getenv("OPENHAB_URL", "http://localhost:8080"),
            openhab_token=os.getenv("OPENHAB_TOKEN"),
            timeout=int(os.getenv("OPENHAB_TIMEOUT", "30")),
            retry_attempts=int(os.getenv("OPENHAB_RETRY_ATTEMPTS", "3")),
            retry_backoff_factor=float(os.getenv("OPENHAB_RETRY_BACKOFF_FACTOR", "2.0")),
            retry_max_delay=int(os.getenv("OPENHAB_RETRY_MAX_DELAY", "60")),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'Config':
        """Load configuration from JSON file.
        
        Args:
            config_path: Path to JSON configuration file
            
        Returns:
            Config instance loaded from file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
            ValueError: If config values are invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in config file: {e}", e.doc, e.pos)
        
        # Extract relevant configuration values
        return cls(
            openhab_url=config_data.get("openhab_url", "http://localhost:8080"),
            openhab_token=config_data.get("openhab_token"),
            timeout=config_data.get("timeout", 30),
            retry_attempts=config_data.get("retry_attempts", 3),
            retry_backoff_factor=config_data.get("retry_backoff_factor", 2.0),
            retry_max_delay=config_data.get("retry_max_delay", 60),
            log_level=config_data.get("log_level", "INFO")
        )
    
    @classmethod
    def from_env_and_file(cls, config_path: Optional[Path] = None) -> 'Config':
        """Load configuration from environment variables and optional file.
        
        Environment variables take precedence over file values.
        
        Args:
            config_path: Optional path to JSON configuration file
            
        Returns:
            Config instance with merged configuration
        """
        # Start with file-based config if available
        if config_path and config_path.exists():
            try:
                config = cls.from_file(config_path)
                logger = logging.getLogger(__name__)
                logger.info(f"Loaded configuration from file: {config_path}")
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to load config file {config_path}: {e}")
                config = cls()
        else:
            config = cls()
        
        # Override with environment variables if set
        env_overrides = {}
        
        if os.getenv("OPENHAB_URL"):
            env_overrides["openhab_url"] = os.getenv("OPENHAB_URL")
        
        if os.getenv("OPENHAB_TOKEN"):
            env_overrides["openhab_token"] = os.getenv("OPENHAB_TOKEN")
        
        if os.getenv("OPENHAB_TIMEOUT"):
            env_overrides["timeout"] = int(os.getenv("OPENHAB_TIMEOUT"))
        
        if os.getenv("OPENHAB_RETRY_ATTEMPTS"):
            env_overrides["retry_attempts"] = int(os.getenv("OPENHAB_RETRY_ATTEMPTS"))
        
        if os.getenv("OPENHAB_RETRY_BACKOFF_FACTOR"):
            env_overrides["retry_backoff_factor"] = float(os.getenv("OPENHAB_RETRY_BACKOFF_FACTOR"))
        
        if os.getenv("OPENHAB_RETRY_MAX_DELAY"):
            env_overrides["retry_max_delay"] = int(os.getenv("OPENHAB_RETRY_MAX_DELAY"))
        
        if os.getenv("LOG_LEVEL"):
            env_overrides["log_level"] = os.getenv("LOG_LEVEL")
        
        # Apply environment overrides
        if env_overrides:
            config_dict = config.dict()
            config_dict.update(env_overrides)
            config = cls(**config_dict)
        
        return config


# Global configuration instance
_config: Optional[Config] = None


def get_config(config_path: Optional[Path] = None) -> Config:
    """Get the global configuration instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Global configuration instance
    """
    global _config
    if _config is None:
        # Check for default config file locations in Docker environment
        default_paths = [
            Path("/app/config.json"),  # Docker volume mount
            Path("/app/config/config.json"),  # Docker config directory
            Path("config.json"),  # Local development
        ]
        
        # Use provided path or find default
        if config_path:
            _config = Config.from_env_and_file(config_path)
        else:
            # Try default locations
            config_file = None
            for path in default_paths:
                if path.exists():
                    config_file = path
                    break
            
            _config = Config.from_env_and_file(config_file)
    
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance (mainly for testing)."""
    global _config
    _config = config