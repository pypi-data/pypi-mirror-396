"""
Configuration management for NSMBL MCP server.

Loads configuration from environment variables and optional JSON config file.
"""

import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """
    Configuration for NSMBL MCP server.
    
    Loads from environment variables with optional JSON config for preferences.
    """
    
    def __init__(self) -> None:
        """Initialize configuration from environment and optional config file."""
        # Load .env file if it exists
        load_dotenv()
        
        # Required configuration
        self.api_key = self._get_required_env("NSMBL_API_KEY")
        
        # Optional configuration with defaults
        self.api_base_url = os.getenv(
            "NSMBL_API_BASE_URL", 
            "https://api.nsmbl.io/api/v1"
        )
        
        self.request_timeout = int(os.getenv("NSMBL_REQUEST_TIMEOUT", "30"))
        self.backtest_poll_interval = int(os.getenv("NSMBL_BACKTEST_POLL_INTERVAL", "5"))
        self.backtest_default_timeout = int(os.getenv("NSMBL_BACKTEST_DEFAULT_TIMEOUT", "300"))
        
        # Load optional JSON config for additional preferences
        self._load_json_config()
        
        # Validate configuration
        self._validate()
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise clear error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(
                f"Missing required environment variable: {key}\n"
                f"Please set {key} in your .env file or environment.\n"
                f"See .env.example for configuration template."
            )
        return value
    
    def _load_json_config(self) -> None:
        """Load optional JSON configuration file."""
        config_path = Path.home() / ".nsmbl" / "mcp-config.json"
        
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    json_config = json.load(f)
                
                # Override with JSON config values if present
                if "request_timeout" in json_config:
                    self.request_timeout = json_config["request_timeout"]
                if "backtest_poll_interval" in json_config:
                    self.backtest_poll_interval = json_config["backtest_poll_interval"]
                if "backtest_default_timeout" in json_config:
                    self.backtest_default_timeout = json_config["backtest_default_timeout"]
                    
            except json.JSONDecodeError as e:
                # Don't fail on invalid JSON, just ignore it
                print(f"Warning: Invalid JSON in config file {config_path}: {e}")
            except Exception as e:
                print(f"Warning: Could not load config file {config_path}: {e}")
    
    def _validate(self) -> None:
        """Validate configuration values."""
        if not self.api_base_url.startswith(("http://", "https://")):
            raise ValueError(
                f"Invalid API base URL: {self.api_base_url}\n"
                f"URL must start with http:// or https://"
            )
        
        if self.request_timeout <= 0:
            raise ValueError(
                f"Invalid request timeout: {self.request_timeout}\n"
                f"Timeout must be a positive number"
            )
        
        if self.backtest_poll_interval <= 0:
            raise ValueError(
                f"Invalid backtest poll interval: {self.backtest_poll_interval}\n"
                f"Poll interval must be a positive number"
            )
        
        if self.backtest_default_timeout <= 0:
            raise ValueError(
                f"Invalid backtest default timeout: {self.backtest_default_timeout}\n"
                f"Timeout must be a positive number"
            )
    
    def get_auth_header(self) -> dict[str, str]:
        """Get authentication header for API requests."""
        return {"Authorization": f"Bearer {self.api_key}"}
    
    def __repr__(self) -> str:
        """String representation (hides API key)."""
        return (
            f"Config("
            f"api_base_url='{self.api_base_url}', "
            f"api_key='***', "
            f"request_timeout={self.request_timeout}, "
            f"backtest_poll_interval={self.backtest_poll_interval}, "
            f"backtest_default_timeout={self.backtest_default_timeout}"
            f")"
        )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get or initialize global config instance.
    
    Returns:
        Config: Global configuration instance
        
    Raises:
        ValueError: If required configuration is missing or invalid
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config() -> None:
    """Reset global config instance (useful for testing)."""
    global _config
    _config = None

