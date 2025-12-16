"""
Configuration management for warpdata.

Configuration is loaded with the following precedence:
1. Function arguments (highest priority)
2. Environment variables
3. config.toml file
4. Library defaults (lowest priority)
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import toml

from .utils import get_warpdata_home, expand_path, ensure_dir


class Config:
    """
    Warpdata configuration manager.
    """

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to config.toml file (optional)
        """
        self._config: Dict[str, Any] = {}
        self._load_defaults()

        # Load config file if it exists
        if config_file is None:
            config_file = get_warpdata_home() / "config.toml"

        if Path(config_file).exists():
            self._load_config_file(config_file)

        # Override with environment variables
        self._load_env_vars()

    def _load_defaults(self):
        """Load default configuration values."""
        warpdata_home = get_warpdata_home()

        self._config = {
            "core": {
                "cache_dir": str(warpdata_home / "cache"),
                "registry_db": str(warpdata_home / "registry.db"),
                "profile": "default",
                # Default workspace used when one isn't specified explicitly
                # e.g., warpdata://my-dataset => warpdata://{default_workspace}/my-dataset
                "default_workspace": "local",
                # Whether wd.load should attempt to fetch raw data automatically
                "ensure_raw_on_load": False,
                # Optional size guard (bytes) when auto-fetching raw data
                "ensure_raw_max_bytes": None,
                # Upload chunk size for multipart uploads (MB)
                # Larger = faster but less resume granularity. Max 5000 (5GB S3 limit)
                "upload_chunk_mb": 5000,
            },
            "profiles": {
                "default": {
                    "s3": {
                        "anon": False,
                        "region_name": "us-east-1",
                    },
                    "hf": {},
                }
            },
        }

    def _load_config_file(self, config_file: Path):
        """
        Load configuration from TOML file.

        Args:
            config_file: Path to config file
        """
        try:
            file_config = toml.load(config_file)
            self._merge_config(self._config, file_config)
        except Exception as e:
            # Log warning but don't fail - use defaults
            pass

    def _load_env_vars(self):
        """Load configuration from environment variables."""
        # Cache directory
        if cache_dir := os.getenv("WARPDATA_CACHE_DIR"):
            self._config["core"]["cache_dir"] = cache_dir

        # Registry database
        if registry_db := os.getenv("WARPDATA_REGISTRY_DB"):
            self._config["core"]["registry_db"] = registry_db

        # Profile
        if profile := os.getenv("WARPDATA_PROFILE"):
            self._config["core"]["profile"] = profile

        # Default workspace for shorthand dataset IDs
        if default_ws := os.getenv("WARPDATA_DEFAULT_WORKSPACE"):
            self._config["core"]["default_workspace"] = default_ws

        # Auto-fetch raw data on load
        if ensure_raw := os.getenv("WARPDATA_LOAD_RAW"):
            self._config["core"]["ensure_raw_on_load"] = ensure_raw.lower() in ("1", "true", "yes", "y")
        if ensure_raw_max := os.getenv("WARPDATA_LOAD_RAW_MAX_BYTES"):
            try:
                self._config["core"]["ensure_raw_max_bytes"] = int(ensure_raw_max)
            except ValueError:
                pass

        # Upload chunk size (MB) - for multipart uploads
        if chunk_mb := os.getenv("WARPDATA_UPLOAD_CHUNK_MB"):
            try:
                self._config["core"]["upload_chunk_mb"] = min(5000, max(5, int(chunk_mb)))
            except ValueError:
                pass

        # AWS credentials
        if aws_key := os.getenv("AWS_ACCESS_KEY_ID"):
            self._ensure_profile_section("s3")
            self._config["profiles"][self.profile]["s3"]["aws_access_key_id"] = aws_key

        if aws_secret := os.getenv("AWS_SECRET_ACCESS_KEY"):
            self._ensure_profile_section("s3")
            self._config["profiles"][self.profile]["s3"]["aws_secret_access_key"] = aws_secret

        if aws_region := os.getenv("AWS_REGION"):
            self._ensure_profile_section("s3")
            self._config["profiles"][self.profile]["s3"]["region_name"] = aws_region

        # Hugging Face token
        if hf_token := os.getenv("HF_TOKEN"):
            self._ensure_profile_section("hf")
            self._config["profiles"][self.profile]["hf"]["token"] = hf_token

    def _ensure_profile_section(self, section: str):
        """Ensure a profile section exists."""
        profile = self.profile
        if profile not in self._config["profiles"]:
            self._config["profiles"][profile] = {}
        if section not in self._config["profiles"][profile]:
            self._config["profiles"][profile][section] = {}

    def _merge_config(self, base: Dict, override: Dict):
        """
        Recursively merge override config into base config.

        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    @property
    def cache_dir(self) -> Path:
        """Get the cache directory path."""
        path = expand_path(self._config["core"]["cache_dir"])
        return ensure_dir(path)

    @property
    def registry_db(self) -> Path:
        """Get the registry database path."""
        path = expand_path(self._config["core"]["registry_db"])
        # Ensure parent directory exists
        ensure_dir(path.parent)
        return path

    @property
    def profile(self) -> str:
        """Get the active profile name."""
        return self._config["core"]["profile"]

    @property
    def default_workspace(self) -> str:
        """Get the default workspace name for shorthand URIs."""
        return self._config["core"].get("default_workspace", "local")

    @property
    def upload_chunk_mb(self) -> int:
        """Get upload chunk size in MB for multipart uploads."""
        return self._config["core"].get("upload_chunk_mb", 5000)

    def get_profile_config(self, service: str) -> Dict[str, Any]:
        """
        Get configuration for a specific service in the active profile.

        Args:
            service: Service name (e.g., 's3', 'hf')

        Returns:
            Configuration dictionary for the service
        """
        profile = self.profile
        if profile in self._config["profiles"]:
            return self._config["profiles"][profile].get(service, {})
        return {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-separated key.

        Args:
            key: Configuration key (e.g., 'core.cache_dir')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        parts = key.split(".")
        value = self._config

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Config instance
    """
    global _global_config

    if _global_config is None:
        _global_config = Config()

    return _global_config


def reset_config():
    """Reset the global configuration (useful for testing)."""
    global _global_config
    _global_config = None
