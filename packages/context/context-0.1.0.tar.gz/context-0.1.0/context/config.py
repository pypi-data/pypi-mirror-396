"""Configuration loading for context."""

import os
from dataclasses import dataclass
from typing import Optional

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


@dataclass
class Config:
    """context configuration."""
    remote_url: Optional[str] = None
    api_key: Optional[str] = None
    tenant: str = "default_tenant"
    database: str = "default_database"
    local_path: Optional[str] = None

    @classmethod
    def config_path(cls) -> str:
        """Get the config file path."""
        # macOS: ~/Library/Application Support/cvfs/config.toml
        # Linux: ~/.config/cvfs/config.toml
        # Windows: %APPDATA%/cvfs/config.toml
        if os.name == "nt":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        elif hasattr(os, "uname") and os.uname().sysname == "Darwin":
            base = os.path.expanduser("~/Library/Application Support")
        else:
            base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        return os.path.join(base, "cvfs", "config.toml")

    @classmethod
    def load(cls) -> "Config":
        """Load config from file."""
        path = cls.config_path()
        if not os.path.exists(path):
            return cls()

        if tomllib is None:
            # Fallback: simple TOML parsing for basic key=value
            data = {}
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        data[key] = value
        else:
            with open(path, "rb") as f:
                data = tomllib.load(f)

        return cls(
            remote_url=data.get("remote_url"),
            api_key=data.get("api_key"),
            tenant=data.get("tenant", "default_tenant"),
            database=data.get("database", "default_database"),
            local_path=data.get("local_path"),
        )

    def get_url(self) -> str:
        """Get Chroma URL."""
        if self.remote_url:
            return self.remote_url
        return "http://localhost:8000"

    def is_configured(self) -> bool:
        """Check if config is set up."""
        return self.remote_url is not None or self.local_path is not None
