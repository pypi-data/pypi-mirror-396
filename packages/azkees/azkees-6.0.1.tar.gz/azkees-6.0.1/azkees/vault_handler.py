"""Vault handler that centralizes all vault operations."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

from azkees.az import Az, KeyNotFoundError
from azkees.logger_setup import log


class VaultHandler:
    """
    Central class to manage all interactions with Azure Key Vault via Az.
    Provides:
    - Secret retrieval and listing
    - Secret setting and deletion
    - Secret purging and recovery
    - Secure URL logging with redaction
    """

    def __init__(self, section: str, keys_config_path: Optional[str] = None):
        """
        Initialize VaultHandler with optional explicit config path for Docker volume support.
        
        Args:
            section (str): Configuration section name from api_keys.ini
            keys_config_path (str, optional): Path to api_keys.ini file.
                If not provided, falls back to environment variables.
                For Docker: /app/config/api_keys.ini
        """
        self.section = section
        try:
            self.az_client = Az(config_section=section, keys_config_path=keys_config_path)
            log.debug("VaultHandler initialized for section: %s", section)
        except (FileNotFoundError, ValueError) as e:
            log.critical("Invalid or missing config file/section: %s", e)
            raise
        except Exception as e:
            log.critical("Unexpected error initializing Az client for section %s: %s", section, e)
            raise

    def get_secret(self, key: str) -> str:
        """
        Retrieve a single secret value.

        Args:
            key (str): The name of the secret to retrieve.

        Returns:
            str: The secret value.

        Raises:
            KeyNotFoundError: If the secret does not exist.
            ResourceNotFoundError: If the vault resource is not found.
            HttpResponseError: If there's an API error.
        """
        try:
            secret = self.az_client.get_secrets(key).get("value")
            if not secret:
                raise KeyNotFoundError(f"No value returned for key: {key}")
            return secret
        except KeyNotFoundError:
            log.critical("Vault key not found: %s in section: %s", key, self.section)
            raise
        except ResourceNotFoundError:
            log.error("Azure Key Vault resource not found for key: %s", key)
            raise
        except HttpResponseError as e:
            log.error("HTTP error while accessing key '%s': %s", key, e.message)
            raise

    def get_multiple_secrets(self, keys: List[str]) -> dict[str, str]:
        """
        Retrieve multiple secrets at once using concurrent operations.

        Args:
            keys (List[str]): List of secret names to retrieve.

        Returns:
            dict[str, str]: Dictionary mapping secret names to their values.
            Only includes successfully retrieved secrets.

        Note:
            This method uses concurrent operations to improve performance.
            Failed retrievals are logged but don't stop other operations.
        """
        def fetch_secret(key):
            """Fetch a single secret, returning (key, value) or (key, None) if failed."""
            try:
                return key, self.get_secret(key)
            except Exception as exc:
                log.warning("Failed to retrieve secret '%s': %s", key, exc)
                return key, None

        secrets = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_key = {executor.submit(fetch_secret, key): key for key in keys}

            for future in as_completed(future_to_key):
                key, value = future.result()
                if value is not None:
                    secrets[key] = value

        return secrets

    def set_secret(self, key: str, value: str) -> bool:
        """
        Set a secret value into the Azure Key Vault.

        Args:
            key (str): The name of the secret.
            value (str): The value to store.

        Returns:
            bool: True if successful.

        Raises:
            HttpResponseError: If there's an error setting the secret.
        """
        try:
            result = self.az_client.set_secrets(name=key, value=value)
            if result:
                log.info("Secret '%s' set successfully in section: %s", key, self.section)
            return result
        except HttpResponseError as e:
            log.error("Failed to set key '%s': %s", key, e.message)
            raise

    def list_secrets(self) -> List[str]:
        """
        List all secrets in the vault.

        Returns:
            List[str]: List of secret names.

        Raises:
            HttpResponseError: If there's an error accessing the vault.
        """
        try:
            all_secrets = list(
                self.az_client.secret_client.list_properties_of_secrets()
            )
            # Only return enabled secrets that aren't scheduled for deletion
            valid_secrets = [
                str(secret.name)
                for secret in all_secrets
                if secret.enabled and not getattr(secret, "recovery_id", None)
            ]
            log.debug("Found %d secrets in vault", len(valid_secrets))
            return valid_secrets
        except HttpResponseError as e:
            log.error("Failed to list secrets: %s", e.message)
            raise

    def purge_secret(self, key: str) -> bool:
        """
        Permanently removes a secret from the vault that has been deleted.

        This method will:
        1. Purge the secret (permanently removes it)
        2. Wait for purge to complete

        Args:
            key (str): The name of the secret to purge.

        Returns:
            bool: True if successfully purged.

        Raises:
            HttpResponseError: If there's an error during purging.
        """
        try:
            # Purge the secret
            self.az_client.secret_client.purge_deleted_secret(key)
            log.info("Secret '%s' purge initiated", key)

            # Wait for purge to complete (check if we can still get the deleted secret)
            max_retries = 30
            retry_delay = 1  # second
            for attempt in range(max_retries):
                try:
                    self.az_client.secret_client.get_deleted_secret(key)
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    log.warning("Secret '%s' still exists after purge", key)
                    return False
                except ResourceNotFoundError:
                    # This is good - means the secret is fully purged
                    log.info("Secret '%s' purged successfully", key)
                    return True

            return False

        except ResourceNotFoundError:
            # If the secret is already purged, that's fine
            log.info("Secret '%s' already purged", key)
            return True
        except HttpResponseError as e:
            log.error("Failed to purge secret '%s': %s", key, e.message)
            raise

    def delete_secret(self, key: str, purge: bool = False) -> bool:
        """
        Delete a secret from the vault with optional purging.

        This method will:
        1. Delete the secret (moves to soft-deleted state)
        2. Optionally purge the secret if purge=True

        Args:
            key (str): The name of the secret to delete.
            purge (bool, optional): Whether to purge the secret after deletion.
                Defaults to False.

        Returns:
            bool: True if successfully deleted (and purged if requested).

        Raises:
            HttpResponseError: If there's an error during deletion.
        """
        try:
            # First try to delete the secret
            poller = self.az_client.secret_client.begin_delete_secret(key)
            # Wait for the delete operation to complete
            deleted_secret = poller.result()

            # Log deletion status
            log.info("Secret '%s' deleted (soft-delete)", key)

            # Log the properties we know are available
            log.info(" - Name: %s", deleted_secret.name)
            log.info(" - ID: %s", deleted_secret.id)

            # Safely check and log scheduled purge date
            purge_date = getattr(deleted_secret, "scheduled_purge_date", None)
            if purge_date:
                log.info(" - Scheduled Purge Date: %s", purge_date)
                # Log approximate days until purge based on scheduled date
                try:
                    now = datetime.now(timezone.utc)
                    if purge_date.tzinfo:
                        days_until = (purge_date - now).days
                        log.info(" - Days until purge: %d", days_until)
                except (TypeError, AttributeError, ValueError) as e:
                    # TypeError: If dates are not compatible for subtraction
                    # AttributeError: If date object lacks required methods
                    # ValueError: If date arithmetic fails
                    log.debug("Could not calculate days until purge: %s", str(e))

            if purge:
                return self.purge_secret(key)

            return True

        except ResourceNotFoundError:
            # If the secret doesn't exist, that's fine
            log.info("Secret '%s' not found - already deleted", key)
            return True
        except HttpResponseError as e:
            log.error("Failed to delete secret '%s': %s", key, e.message)
            raise

    @staticmethod
    def mask_sensitive_info(url: str, sensitive_keys: Optional[List[str]] = None) -> str:
        """
        Masks passwords in URLs and sensitive query parameters.

        Examples:
            >>> vh = VaultHandler("section")
            >>> vh.mask_sensitive_info("postgresql://user:pass@host:5432")
            'postgresql://user:****@host:5432'
            >>> vh.mask_sensitive_info("https://api.com?token=xyz&name=test")
            'https://api.com?token=****&name=test'

        Args:
            url (str): The URL to redact.
            sensitive_keys (Optional[List[str]]): List of query keys to mask.
                Defaults to ['apikey', 'token', 'access_token', 'secret', 'password'].

        Returns:
            str: Redacted URL string with sensitive information masked.
        """
        # Delegate to Az.mask_sensitive_info for consistent implementation
        from azkees.az import Az
        return Az.mask_sensitive_info(url, sensitive_keys)
