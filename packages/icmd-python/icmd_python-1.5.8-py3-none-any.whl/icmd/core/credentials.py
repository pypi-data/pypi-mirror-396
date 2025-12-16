"""Credential management for ICMD client."""

import base64
import hashlib
import json
import logging
import platform
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class CredentialManager:
    """Handles domain-keyed credential persistence for multiple ICMD instances."""

    def __init__(self, credential_file: str | None = None):
        """Initialize credential manager.

        Args:
            credential_file: Optional custom path to credential file.
                           Defaults to ~/.icmd/credentials.json
        """
        if credential_file:
            self.credential_file = Path(credential_file)
        else:
            icmd_dir = Path.home() / ".icmd"
            self.credential_file = icmd_dir / "credentials.json"

        self._cipher = None

    def _get_cipher(self) -> Fernet:
        """Get or create Fernet cipher with machine-specific key.

        Returns
        -------
            Fernet cipher instance for encryption/decryption
        """
        if self._cipher is None:
            # Derive encryption key from machine-specific data
            machine_id = f"{platform.node()}-{platform.system()}-{Path.home()}"
            key_material = hashlib.sha256(machine_id.encode()).digest()
            # Fernet requires base64-encoded 32-byte key
            key = base64.urlsafe_b64encode(key_material)
            self._cipher = Fernet(key)
        return self._cipher

    def load_domain_credentials(self, domain: str) -> dict[str, Any]:
        """Load cached credentials for specific domain.

        Args:
            domain: Domain to load credentials for

        Returns
        -------
            Dictionary containing auth_method, refresh_token, etc.
            Empty dict if file doesn't exist or domain not found.
        """
        all_credentials = self._load_all_credentials()
        return all_credentials.get(domain, {})

    def _load_all_credentials(self) -> dict[str, dict[str, Any]]:
        """Load all domain-keyed credentials from file.

        Returns
        -------
            Dictionary with domain keys and credential values.
            Empty dict if file doesn't exist or can't be read.
        """
        if not self.credential_file.exists():
            return {}

        try:
            with open(self.credential_file, "rb") as f:
                encrypted_data = f.read()

            # Decrypt the data
            cipher = self._get_cipher()
            decrypted_data = cipher.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode("utf-8"))

            # Validate domain-keyed structure
            if not isinstance(data, dict):
                logger.warning("Credential file contains invalid data structure")
                return {}

            return data

        except (json.JSONDecodeError, OSError, Exception) as e:
            logger.warning(f"Failed to load credential file: {e}")
            return {}

    def save_domain_credentials(
        self, domain: str, auth_method: str, refresh_token: str, **additional_data: Any
    ) -> None:
        """Save credentials for specific domain, preserving other domains.

        Args:
            domain: ICMD domain
            auth_method: Authentication method (SAML/PASSWORD)
            refresh_token: Refresh token for subsequent sessions
            **additional_data: Additional data to store
        """
        # Load existing credentials
        all_credentials = self._load_all_credentials()

        # Update credentials for this domain
        all_credentials[domain] = {
            "auth_method": auth_method,
            "refresh_token": refresh_token,
            "saved_at": datetime.now(UTC).isoformat(),
            **additional_data,
        }

        self._save_all_credentials(all_credentials)

    def _save_all_credentials(self, all_credentials: dict[str, dict[str, Any]]) -> None:
        """Save all domain-keyed credentials to file.

        Args:
            all_credentials: Dictionary with domain keys and credential values
        """
        try:
            # Ensure parent directory exists with secure permissions
            self.credential_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

            # Encrypt the data
            cipher = self._get_cipher()
            json_data = json.dumps(all_credentials, indent=2)
            encrypted_data = cipher.encrypt(json_data.encode("utf-8"))

            # Save with proper permissions (readable only by user)
            with open(self.credential_file, "wb") as f:
                f.write(encrypted_data)

            # Set file permissions to be readable only by user
            self.credential_file.chmod(0o600)

            logger.debug(f"Saved credentials to {self.credential_file}")

        except OSError as e:
            logger.error(f"Failed to save credentials: {e}")
            # Don't raise - failing to save credentials shouldn't break the session

    def clear_session_data(self) -> None:
        """Clear cached session data by removing the credential file."""
        try:
            if self.credential_file.exists():
                self.credential_file.unlink()
                logger.info("Cleared cached credentials")
        except OSError as e:
            logger.warning(f"Failed to clear credentials: {e}")

    def get_auth_method(self, domain: str) -> str | None:
        """Get cached authentication method for domain."""
        data = self.load_domain_credentials(domain)
        return data.get("auth_method")

    def get_refresh_token(self, domain: str) -> str | None:
        """Get cached refresh token for domain."""
        data = self.load_domain_credentials(domain)
        return data.get("refresh_token")

    def clear_refresh_token(self, domain: str) -> None:
        """Clear only the refresh token for domain, keeping other session data."""
        all_credentials = self._load_all_credentials()
        if domain in all_credentials and "refresh_token" in all_credentials[domain]:
            all_credentials[domain].pop("refresh_token")
            self._save_all_credentials(all_credentials)
            logger.debug(f"Cleared invalid refresh token for domain {domain}")

    def clear_domain_credentials(self, domain: str) -> None:
        """Clear all credentials for specific domain."""
        all_credentials = self._load_all_credentials()
        if domain in all_credentials:
            del all_credentials[domain]
            self._save_all_credentials(all_credentials)
            logger.info(f"Cleared credentials for domain {domain}")
