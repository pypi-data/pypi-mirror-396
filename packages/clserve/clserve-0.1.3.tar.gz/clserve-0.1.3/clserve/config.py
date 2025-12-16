"""User configuration management for clserve."""

import subprocess
from dataclasses import dataclass, fields
from pathlib import Path

import yaml


CLSERVE_DIR = Path.home() / ".clserve"
CONFIG_FILE = CLSERVE_DIR / "config.yaml"


@dataclass
class UserConfig:
    """User configuration for clserve defaults."""

    account: str = ""
    partition: str = "normal"
    environment: str = "sglang_gb200"
    router_environment: str = "sglang_router"
    time_limit: str = "04:00:00"

    def to_dict(self) -> dict:
        """Convert config to dictionary for YAML serialization."""
        return {f.name: getattr(self, f.name) for f in fields(self)}


def get_default_account() -> str:
    """Get the default cluster account from system."""
    try:
        result = subprocess.run(
            ["id", "-gn"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def load_config() -> UserConfig:
    """Load user configuration from ~/.clserve/config.yaml.

    Returns:
        UserConfig with values from file or defaults
    """
    if not CONFIG_FILE.exists():
        return UserConfig()

    try:
        with open(CONFIG_FILE, "r") as f:
            data = yaml.safe_load(f) or {}
        return UserConfig(
            account=data.get("account", ""),
            partition=data.get("partition", "normal"),
            environment=data.get("environment", "sglang_gb200"),
            router_environment=data.get("router_environment", "sglang_router"),
            time_limit=data.get("time_limit", "04:00:00"),
        )
    except Exception:
        return UserConfig()


def save_config(config: UserConfig) -> None:
    """Save user configuration to ~/.clserve/config.yaml.

    Args:
        config: UserConfig to save
    """
    CLSERVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False, sort_keys=False)


def get_account() -> str:
    """Get the cluster account, preferring config over system default.

    Returns:
        Account name from config if set, otherwise from system
    """
    config = load_config()
    if config.account:
        return config.account
    return get_default_account() or "infra01"
