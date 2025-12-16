"""Configuration management for DUTVulnScanner."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def get_config_dir() -> Path:
    """Get the configuration directory path."""
    config_dir = Path.home() / ".dutVulnScanner"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_profiles_dir() -> Path:
    """Get the profiles directory path."""
    import dutVulnScanner

    # Get the package directory
    package_dir = Path(dutVulnScanner.__file__).parent
    profiles_dir = package_dir / "profiles"

    # If package profiles exist, use them
    if profiles_dir.exists():
        return profiles_dir

    # Fall back to workspace profiles (for development)
    workspace_profiles = Path("dutVulnScanner/profiles")
    if workspace_profiles.exists():
        return workspace_profiles

    # Last resort: user config
    profiles_dir = get_config_dir() / "profiles"
    profiles_dir.mkdir(exist_ok=True)
    return profiles_dir


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from file.

    Args:
        config_path: Optional path to config file. If not provided, uses default.

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = get_config_dir() / "config.yaml"

    if not config_path.exists():
        return get_default_config()

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config or get_default_config()


def save_config(config: Dict[str, Any], config_path: Optional[Path] = None):
    """Save configuration to file."""
    if config_path is None:
        config_path = get_config_dir() / "config.yaml"

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, default_flow_style=False)


def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    return {
        "runners": {
            "local": {
                "enabled": True,
                "timeout": 3600,
            },
            "ssh": {
                "enabled": True,
                "default_port": 22,
                "timeout": 3600,
            },
            "docker": {
                "enabled": True,
                "default_image": "dutVulnScanner:latest",
                "timeout": 3600,
            },
        },
        "adapters": {
            "nmap": {
                "enabled": True,
                "path": "nmap",
                "default_args": ["-sV", "-sC"],
            },
            "nuclei": {
                "enabled": True,
                "path": "nuclei",
                "templates_dir": None,
            },
            "whatweb": {
                "enabled": True,
                "path": "whatweb",
            },
        },
        "reporting": {
            "default_format": "html",
            "output_dir": "reports",
            "pdf_enabled": True,
            "ai_summary_enabled": True,
        },
        "ai": {
            "enabled": True,
            "provider": "gemini",
            "model": "gemini-2.5-flash",
        },
        "correlation": {
            "enabled": True,
            "confidence_threshold": 0.7,
        },
    }


def load_profile(profile_name: str) -> Dict[str, Any]:
    """
    Load a scan profile.

    Args:
        profile_name: Name of the profile (without .yaml extension)

    Returns:
        Profile configuration dictionary

    Raises:
        FileNotFoundError: If profile doesn't exist
    """
    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / f"{profile_name}.yaml"

    if not profile_path.exists():
        raise FileNotFoundError(f"Profile '{profile_name}' not found at {profile_path}")

    with open(profile_path, "r", encoding="utf-8") as f:
        profile = yaml.safe_load(f)

    return profile
