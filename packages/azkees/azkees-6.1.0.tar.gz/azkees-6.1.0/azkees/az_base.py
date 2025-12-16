"""
Base Azure Key Vault client used to initialize and retrieve secrets without logger dependency.
"""

import os
from configparser import ConfigParser
from typing import Optional

from azure.core.exceptions import AzureError
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient


class AzBase:
    """
    Base class for accessing Azure Key Vault secrets.

    Parameters:
        config_section (str): The section in the .ini config file to read Azure credentials from.
        keys_config_path (str, optional): Path to the .ini configuration file. 
            If not provided, falls back to environment variables (keys_config_windows/keys_config_linux).
            This supports Docker volume mounts: /app/config/api_keys.ini
    """

    def __init__(self, config_section: str, keys_config_path: Optional[str] = None):
        self.section = config_section
        
        # Support explicit path for Docker volume mounts, or fall back to environment variables
        if keys_config_path is None:
            try:
                from azkees.load_envs import keys_config
                keys_config_path = keys_config
            except (ImportError, KeyError) as e:
                raise ValueError(
                    "Either provide keys_config_path parameter or set "
                    "keys_config_windows/keys_config_linux environment variables"
                ) from e
        
        self.keys_config_path = keys_config_path
        self.secret_client = self.get_azure_secrets_client(self.keys_config_path, self.section)

    @staticmethod
    def get_azure_secrets_client(config_path: str, section: str) -> SecretClient:
        """
        Create and return an Azure Key Vault SecretClient.

        Args:
            config_path (str): Path to the .ini configuration file.
            section (str): Config section to read credentials from.

        Returns:
            SecretClient: Initialized Azure secret client.
        
        Raises:
            FileNotFoundError: If the config file doesn't exist.
            ValueError: If required configuration values are missing.
        """
        # Initialize the Parser.
        parser = ConfigParser()

        # Read the file.
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        parser.read(config_path)
        
        if not parser.has_section(section):
            raise ValueError(f"Configuration section '{section}' not found in {config_path}")

        # Grab the Azure Credentials needed.
        try:
            tenant_id = parser.get(section, 'azure_tenant_id')
            client_id = parser.get(section, 'azure_client_id')
            client_secret = parser.get(section, 'azure_client_secret')
            vault_url = parser.get(section, 'azure_vault_url')
        except Exception as e:
            raise ValueError(
                f"Missing required Azure configuration in section '{section}': {e}"
            ) from e

        # Initialize the Credentials.
        default_credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

        # Create a Secret Client.
        secret_client = SecretClient(
            vault_url=vault_url,
            credential=default_credential
        )
        return secret_client

    def get_secret(self, name: str) -> str | None:
        """
        Retrieve a secret value by name.

        Args:
            name (str): Name of the secret.

        Returns:
            str | None: The secret value or None if not found.
        """
        try:
            return self.secret_client.get_secret(name).value
        except AzureError:
            return None


class KeyNotFoundError(Exception):
    """Raised when a secret is not found in Azure Key Vault."""
