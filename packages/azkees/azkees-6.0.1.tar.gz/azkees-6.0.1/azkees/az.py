"""
Wrapper around AzBase that adds logging to secret operations.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, List, Optional
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from azkees.az_base import AzBase, KeyNotFoundError
from azkees.logger_setup import log


class Az(AzBase):
    """
    Extension of AzBase that adds logging for secret operations.
    Features:
    - Secret retrieval and setting with logging
    - Batch secret operations with concurrent execution
    - URL redaction for sensitive data
    """

    def get_secrets(self, name: str) -> dict:
        """
        Retrieve a secret with logging.

        Args:
            name (str): The name of the secret.

        Returns:
            dict: A dictionary with secret name and value.

        Raises:
            KeyNotFoundError: If the secret is not found.
        """
        value = super().get_secret(name)
        if value is None:
            raise KeyNotFoundError(f"Secret '{name}' not found.")
        log.debug("Retrieved secret '%s'", name)
        return {"name": name, "value": value}

    def set_secrets(
        self,
        name: str,
        value: str,
        *,
        enabled: bool | None = None,
        tags: dict[str, str] | None = None,
        content_type: str | None = None,
        not_before: datetime | None = None,
        expires_on: datetime | None = None,
        **kwargs: Any,
    ) -> bool:
        """
        Set a secret in Azure Key Vault with logging.

        Args:
            name (str): The name of the secret.
            value (str): The value of the secret.
            enabled (bool | None, optional): Whether the secret is enabled.
                Defaults to None.
            tags (dict[str, str] | None, optional): Application-specific metadata in the form of
                key-value pairs. Defaults to None.
            content_type (str | None, optional): Type of the secret value such as password,
                certificate, etc. Defaults to None.
            not_before (datetime | None, optional): Not before date of the secret. Defaults to None.
            expires_on (datetime | None, optional): Expiry date of the secret. Defaults to None.
            **kwargs: Additional keyword arguments to be passed to the Azure SDK.

        Returns:
            bool: True if successful.

        Raises:
            KeyNotFoundError: If the operation fails.
        """
        secret = self.secret_client.set_secret(
            name=name,
            value=value,
            enabled=enabled,
            tags=tags,
            content_type=content_type,
            not_before=not_before,
            expires_on=expires_on,
            **kwargs,
        )
        if secret is None:
            raise KeyNotFoundError(f"Failed to set secret '{name}'")
        log.info("Set secret '%s'", name)
        return True

    def get_multiple_secrets(self, names: List[str]) -> dict[str, str]:
        """
        Retrieve multiple secrets at once using concurrent execution for better performance.

        Args:
            names (List[str]): List of secret names to retrieve.

        Returns:
            dict[str, str]: Dictionary mapping secret names to their values.
            Only includes successfully retrieved secrets.

        Notes:
            - Uses ThreadPoolExecutor for concurrent API calls
            - Failed retrievals are logged but don't stop other operations
            - Significantly reduces total API call time for multiple secrets
        """
        def fetch_single_secret(name: str) -> tuple[str, Optional[str]]:
            """Fetch a single secret, returning (name, value) or (name, None) if failed."""
            try:
                result = self.get_secrets(name)
                return name, result["value"]
            except KeyNotFoundError:
                log.error("Failed to retrieve secret '%s'", name)
                return name, None

        secrets = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all secret retrieval tasks
            future_to_name = {
                executor.submit(fetch_single_secret, name): name
                for name in names
            }

            # Collect results as they complete
            for future in as_completed(future_to_name):
                name, value = future.result()
                if value is not None:
                    secrets[name] = value

        return secrets

    @staticmethod
    def mask_sensitive_info(url: str, sensitive_keys: List[str] | None = None) -> str:
        """
        Masks passwords in URLs and sensitive query parameters.

        Examples:
            >>> Az.mask_sensitive_info("postgresql://user:pass@host:5432")
            'postgresql://user:@host:5432'
            >>> Az.mask_sensitive_info("https://api.com?token=xyz&name=test")
            'https://api.com?token=****&name=test'

        Args:
            url (str): The URL to redact.
            sensitive_keys (List[str], optional): List of query keys to mask.
                Defaults to ['apikey', 'token', 'access_token', 'secret', 'password'].

        Returns:
            str: Redacted URL string with sensitive information masked.
        """
        if sensitive_keys is None:
            sensitive_keys = ['apikey', 'token', 'access_token', 'secret', 'password']

        try:
            parsed = urlparse(url)
            
            # Validate URL has proper scheme and netloc for a valid URL
            if not parsed.scheme or not parsed.netloc:
                log.warning("Invalid URL format: %s", url)
                return "<redaction failed>"

            # Redact credentials in netloc
            if parsed.password:
                safe_netloc = f"{parsed.username}:****@{parsed.hostname}"
                if parsed.port:
                    safe_netloc += f":{parsed.port}"
            else:
                safe_netloc = parsed.netloc

            # Redact sensitive query parameters
            query_params = parse_qsl(parsed.query, keep_blank_values=True)
            redacted_query = [
                (k, '****' if k.lower() in sensitive_keys else v)
                for k, v in query_params
            ]

            # Build redacted query string without URL encoding the asterisks
            query_str = '&'.join(
                f"{k}={v}" for k, v in redacted_query
            ) if redacted_query else ''

            redacted_url = urlunparse((
                parsed.scheme,
                safe_netloc,
                parsed.path,
                parsed.params,
                query_str,
                parsed.fragment
            ))

            return redacted_url

        except Exception as e:
            log.warning("URL parse error while redacting: %s", e)
            return "<redaction failed>"
