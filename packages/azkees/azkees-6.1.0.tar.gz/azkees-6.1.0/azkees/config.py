"""Azure Key Vault client implementation with singleton pattern and caching.

This module provides a secure interface for interacting with Azure Key Vault,
implementing a singleton pattern to ensure consistent access across the application.
It handles secret retrieval, caching, and environment-specific configurations.

The client supports:
- Secure secret retrieval with LRU caching
- Singleton pattern for consistent vault access
- Batch secret operations with concurrent execution
- Connection validation and error handling
- Integration with Azure Key Vault through Azkees

Usage:
    client = AzureVaultClient(config_section="my_section", keys_config_path="/app/config/api_keys.ini")
    secret = client.get_secret("my-secret")
    secrets = client.get_secrets_batch(["secret1", "secret2", "secret3"])

Environment Variables:
    KEYS_CONFIG: Path to the API keys configuration file (optional if keys_config_path provided)

Author: Bharani Nitturi
Date: December 2025
"""

from functools import lru_cache
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from azure.core.exceptions import ResourceNotFoundError
from azure.keyvault.secrets import SecretClient

from azkees.az import Az
from azkees.logger_setup import log


class AzureVaultClient:
    """A singleton client for secure interaction with Azure Key Vault.

    This class provides a thread-safe interface to Azure Key Vault with built-in
    caching and environment-specific configurations. It implements the singleton
    pattern to ensure only one vault client exists per application instance.

    Key Features:
    - Singleton pattern for consistent access
    - LRU caching of secret values
    - Batch secret operations with concurrent execution
    - Comprehensive error handling and validation

    Attributes:
        _client (SecretClient): Azure Key Vault SDK client instance
        az_client (Az): Azkees client for extended vault operations
        _is_available (bool): Flag indicating if vault connection is active
        _instance (AzureVaultClient): Singleton instance of the client

    Configuration:
        The client supports two configuration methods:
        1. Explicit path: keys_config_path="/app/config/api_keys.ini" (recommended for Docker)
        2. Environment variable: KEYS_CONFIG (fallback)

    Example:
        >>> client = AzureVaultClient("prod_section", keys_config_path="/app/config/api_keys.ini")
        >>> secret = client.get_secret("api-key")
        >>> is_valid = client.is_available
        >>> secrets = client.get_secrets_batch(["secret1", "secret2"])
    """

    _instance = None
    _client: Optional[SecretClient] = None
    az_client: Optional[Az] = None
    _is_available: bool = False

    def __new__(cls, config_section: str, keys_config_path: Optional[str] = None):
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super(AzureVaultClient, cls).__new__(cls)
            cls._instance._initialize(config_section, keys_config_path)
        return cls._instance

    @property
    def is_available(self) -> bool:
        """Check if vault client is available."""
        return self._is_available

    def _initialize(self, config_section: str, keys_config_path: Optional[str] = None) -> None:
        """Initialize the vault client with the specified configuration.

        This method sets up the Azure Key Vault client with proper credentials and
        configuration. It handles environment-specific setup and validates required
        configuration values.

        Args:
            config_section (str): The configuration section name from api_keys.ini
            keys_config_path (str, optional): Path to the .ini configuration file.
                If not provided, falls back to environment variables.

        Raises:
            ValueError: If required configuration is missing
            Exception: If vault client initialization fails

        Notes:
            - Supports Docker volume mounts: /app/config/api_keys.ini
            - Initializes both Azure SDK client and Azkees client
        """
        if self._client is None:
            try:
                self.az_client = Az(
                    config_section=config_section,
                    keys_config_path=keys_config_path
                )

                # Use the Az client, which already has a fully initialized SecretClient
                self._client = self.az_client.secret_client
                self._is_available = True
                log.info("AzureVaultClient initialized for section: %s", config_section)
            except Exception as e:
                log.error("Failed to initialize AzureVaultClient: %s", e)
                self._is_available = False
                raise

    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str, secret_version: Optional[str] = None) -> str:
        """Retrieve a secret from Azure Key Vault with caching.

        Args:
            secret_name (str): Name of the secret to retrieve.
            secret_version (Optional[str]): Version of the secret. Defaults to None.

        Returns:
            str: The secret value.

        Raises:
            ValueError: If the vault client is not initialized or if secret value is None.
            KeyError: If the secret does not exist in the vault.
        """
        if not self._client:
            raise ValueError("Vault client not initialized")
        try:
            secret = self._client.get_secret(name=secret_name, version=secret_version)
        except ResourceNotFoundError as exc:
            raise KeyError(
                f"Secret '{secret_name}' not found in Azure Key Vault"
            ) from exc
        if secret.value is None:
            raise ValueError(f"Secret '{secret_name}' exists but has no value")
        return str(secret.value)

    def get_secrets_batch(
        self, secret_names: List[str], max_workers: int = 5
    ) -> Dict[str, str]:
        """Retrieve multiple secrets concurrently to reduce API calls.

        Args:
            secret_names (List[str]): List of secret names to retrieve.
            max_workers (int): Maximum number of concurrent threads. Defaults to 5.

        Returns:
            Dict[str, str]: Dictionary mapping secret names to their values.
            Only includes successfully retrieved secrets.

        Notes:
            - Failed retrievals are logged but don't stop other operations
            - Uses ThreadPoolExecutor for concurrent API calls
            - Significantly reduces total API call time
        """
        if not self._client:
            raise ValueError("Vault client not initialized")

        def fetch_single_secret(name: str) -> tuple[str, Optional[str]]:
            """Fetch a single secret, returning (name, value) or (name, None) if failed."""
            try:
                return name, self.get_secret(name)
            except (KeyError, ValueError, ResourceNotFoundError) as exc:
                log.warning("Failed to retrieve secret '%s': %s", name, exc)
                return name, None

        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all secret retrieval tasks
            future_to_name = {
                executor.submit(fetch_single_secret, name): name
                for name in secret_names
            }

            # Collect results as they complete
            for future in as_completed(future_to_name):
                name, value = future.result()
                if value is not None:
                    results[name] = value

        return results

