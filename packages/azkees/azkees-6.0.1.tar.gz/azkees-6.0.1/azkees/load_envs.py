"""
Platform-independent environment configuration loader for AZKees.

This module handles loading configuration paths based on the operating system,
ensuring consistent behavior across different platforms. It determines the
appropriate path for the API keys configuration file based on whether the
system is Windows or Linux.

Example:
    >>> from azkees.load_envs import keys_config
    >>> print(keys_config)
    'C:/path/to/config/api_keys.ini'  # On Windows
    '/app/api_keys.ini'               # On Linux
"""

import os
import platform
from dotenv import load_dotenv

load_dotenv()

IS_WINDOWS = platform.system() == "Windows"

keys_config = os.environ["keys_config_windows" if IS_WINDOWS else "keys_config_linux"]
