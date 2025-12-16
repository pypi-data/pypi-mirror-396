"""Configuration utilities for Claude CLI"""

import os
import sys
from pathlib import Path


def get_config_dir() -> str:
    r"""Get the OS-appropriate config directory for Claude CLI

    Returns:
        Path to the config directory:
        - Windows: %APPDATA%\claude-cli
        - Linux/Mac: ~/.config/claude-cli
    """
    if sys.platform == "win32":
        # Windows: use APPDATA
        base_dir = os.getenv("APPDATA")
        if not base_dir:
            # Fallback to USERPROFILE if APPDATA not set
            base_dir = os.path.expanduser("~")
            config_dir = os.path.join(base_dir, ".claude-cli")
        else:
            config_dir = os.path.join(base_dir, "claude-cli")
    else:
        # Linux/Mac: use XDG_CONFIG_HOME or ~/.config
        xdg_config = os.getenv("XDG_CONFIG_HOME")
        if xdg_config:
            config_dir = os.path.join(xdg_config, "claude-cli")
        else:
            config_dir = os.path.join(os.path.expanduser("~"), ".config", "claude-cli")

    # Create directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    return config_dir
