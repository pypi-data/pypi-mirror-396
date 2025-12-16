"""
AZKees - Azure Key Vault Easy & Secure

A secure and efficient Azure Key Vault client with advanced logging capabilities,
designed for production use with Docker volume support for configuration files.

This package provides:
- Secure secret retrieval with caching
- Batch secret operations with concurrent execution
- Environment-specific configurations
- Comprehensive error handling
- URL masking for sensitive data logging
- Secret lifecycle management (create, update, delete, purge, recover)

Basic Usage:
    >>> from azkees import Az
    >>> client = Az(config_section="production", keys_config_path="/app/config/api_keys.ini")
    >>> secret = client.get_secrets("my-secret")
    >>> print(secret["value"])

Advanced Usage with VaultHandler:
    >>> from azkees import VaultHandler
    >>> vault = VaultHandler(section="production", keys_config_path="/app/config/api_keys.ini")
    >>> secret_value = vault.get_secret("my-secret")
    >>> secrets = vault.get_multiple_secrets(["secret1", "secret2", "secret3"])

Docker Volume Example:
    Mount your api_keys.ini file as a read-only volume:
    
    volumes:
      - /host/path/api_keys.ini:/app/config/api_keys.ini:ro

Author: Bharani Nitturi
License: GPL-3.0
"""

__version__ = "5.0.0"
__author__ = "Bharani Nitturi"
__license__ = "GPL-3.0"

from azkees.az_base import AzBase, KeyNotFoundError
from azkees.az import Az
from azkees.vault_handler import VaultHandler
from azkees.config import AzureVaultClient

__all__ = [
    "AzBase",
    "Az",
    "VaultHandler",
    "AzureVaultClient",
    "KeyNotFoundError",
]
