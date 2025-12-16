"""Configuration module using Rust ClientSettings via PyO3.

This module provides a simple settings() function that returns a cached
ClientSettings instance loaded from ~/.spiral.toml and environment variables.
"""

import functools
import os
from pathlib import Path

import typer

from spiral.core.config import ClientSettings

TEST = "PYTEST_VERSION" in os.environ
CI = "GITHUB_ACTIONS" in os.environ

APP_DIR = Path(typer.get_app_dir("pyspiral"))
LOG_DIR = APP_DIR / "logs"

PACKAGE_NAME = "pyspiral"


@functools.cache
def settings() -> ClientSettings:
    """Get the global ClientSettings instance.

    Configuration is loaded with the following priority (highest to lowest):
    1. Environment variables (SPIRAL__*)
    2. Config file (~/.spiral.toml)
    3. Default values

    Returns:
        ClientSettings: The global configuration instance
    """
    return ClientSettings.load()
