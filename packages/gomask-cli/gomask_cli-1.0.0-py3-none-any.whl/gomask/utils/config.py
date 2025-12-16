"""
Configuration management for GoMask CLI
Handles loading configuration from gomask.toml and environment variables
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Use tomllib for Python 3.11+, tomli for earlier versions
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        # Fallback - will fail gracefully if TOML file is used
        tomllib = None  # type: ignore

from gomask.utils.logger import logger


class Config:
    """Configuration manager for GoMask CLI"""

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._loaded = False

    def load(self, config_path: Optional[Path] = None) -> None:
        """
        Load configuration from gomask.toml and environment variables.

        Priority (highest to lowest):
        1. Environment variables (GOMASK_*)
        2. gomask.toml file
        3. .env file (loaded by dotenv)

        Args:
            config_path: Path to gomask.toml file. If None, searches in current directory
                        and parent directories.
        """
        if self._loaded:
            return

        # Find config file if not specified
        if config_path is None:
            config_path = self._find_config_file()

        # Load from TOML file if it exists
        if config_path and config_path.exists():
            if tomllib is None:
                logger.warning(
                    "TOML support not available. Install 'tomli' package for Python < 3.11"
                )
            else:
                try:
                    with open(config_path, 'rb') as f:
                        toml_data = tomllib.load(f)

                    # Extract gomask section
                    if 'gomask' in toml_data:
                        self._config = toml_data['gomask']
                        
                        logger.debug(f"Loaded configuration from {config_path}")
                except Exception as e:
                    logger.warning(f"Failed to load config from {config_path}: {e}")

        self._loaded = True

    def _find_config_file(self) -> Optional[Path]:
        """
        Search for gomask.toml in current directory and parent directories.

        Returns:
            Path to gomask.toml if found, None otherwise
        """
        current = Path.cwd()

        # Check current directory and up to 3 parent directories
        for _ in range(4):
            config_path = current / 'gomask.toml'
            if config_path.exists():
                return config_path

            parent = current.parent
            if parent == current:  # Reached root
                break
            current = parent

        return None

    def get(self, key: str, default: Any = None, env_var: Optional[str] = None) -> Any:
        """
        Get configuration value.

        Priority:
        1. Environment variable (if env_var specified)
        2. Value from gomask.toml
        3. Default value

        Args:
            key: Configuration key
            default: Default value if not found
            env_var: Environment variable name to check (e.g., 'GOMASK_SECRET')

        Returns:
            Configuration value
        """
        # Check environment variable first (highest priority)
       
        if env_var:
            env_value = os.getenv(env_var)
            if env_value is not None:
                return env_value

        # Check loaded config
        if key in self._config:
            return self._config[key]

        # Return default
        return default

    def get_secret(self) -> Optional[str]:
        """Get API secret from config or environment"""
        return self.get('secret', env_var='GOMASK_SECRET')

    def get_api_url(self) -> str:
        """Get API URL from config or environment"""
        return self.get('api_url', default='https://cli.gomask.ai', env_var='GOMASK_API_URL')

    def get_debug(self) -> bool:
        """Get debug flag from config or environment"""
        debug = self.get('debug', default=False, env_var='GOMASK_DEBUG')

        # Handle string values from environment
        if isinstance(debug, str):
            return debug.lower() in ('true', '1', 'yes', 'on')

        return bool(debug)

    def has_config_file(self) -> bool:
        """Check if a gomask.toml file exists"""
        return self._find_config_file() is not None


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global config instance"""
    global _config
    if _config is None:
        _config = Config()
        _config.load()
    return _config


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from file and environment.

    Args:
        config_path: Optional path to gomask.toml file

    Returns:
        Config instance
    """
    config = get_config()
    if config_path:
        config._loaded = False  # Force reload
        config.load(config_path)
    return config
