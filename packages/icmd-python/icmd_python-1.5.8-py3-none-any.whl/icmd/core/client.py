"""ICMD client - clean, fast, intuitive."""

import contextlib
import webbrowser
from datetime import UTC, datetime, timedelta
from getpass import getpass
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from pathlib import Path

import requests
from requests.adapters import HTTPAdapter

from .credentials import CredentialManager
from .slim_packages import ensure_slim_packages


class ICMDAuthenticationError(Exception):
    """Raised when authentication fails."""


class ICMDConnectionError(Exception):
    """Raised when connection to ICMD fails."""


class ICMDValidationError(Exception):
    """Raised when input validation fails."""


class ICMD:
    """ICMD client - supports multiple domains per process."""

    # Configuration constants
    _DEFAULT_POOL_CONNECTIONS = 20
    _DEFAULT_POOL_MAXSIZE = 20
    _DEFAULT_MAX_RETRIES = 3
    _DEFAULT_TIMEOUT = 30
    _TOKEN_EXPIRE_BUFFER_MS = 5000
    _HTTP_NOT_FOUND = 404
    _REFRESH_TIMEOUT = 10

    # Endpoints excluded from auto-refresh retry
    EXCLUDED_ENDPOINTS: ClassVar[set[str]] = {
        "account/auth/login",
        "account/auth/refresh",
        "account/auth/logout",
        "account/auth/mfa/verify",
        "account/auth/saml/login",
        "account/auth/saml/acs",
    }

    # Session-wide qtpy_slim tracking (shared across all ICMD instances)
    # Prevents loading conflicting package versions within same Python session
    _session_qtpy_version: dict | None = None
    _session_qtpy_server: str | None = None
    _session_qtpy_path: "Path | None" = None

    def __init__(
        self,
        domain: str,
        auth_method: str | None = None,
        developer_token: str | None = None,
        clear_cache: bool = False,
        skip_auth: bool = False,
    ):
        """Initialize ICMD client with required domain parameter.

        Args:
            domain: REQUIRED domain (e.g., 'icmd.questek.com', 'cust.icmd.questek.com')
            auth_method: Override auth method detection. Options: "SAML" or "PASSWORD".
                If not specified, auto-detects based on server config (prefers SAML).
            developer_token: Developer API token for non-interactive use (scripts, CI/CD).
                When provided, skips all authentication flows.
            clear_cache: If True, clears cached credentials before initialization,
                forcing fresh authentication. Useful for switching accounts or
                troubleshooting authentication issues.
            skip_auth: Skip auto-authentication (useful for testing or non-interactive
                environments)

        Raises
        ------
        ValueError
            If domain is not provided or invalid, or if auth_method is invalid
        """
        if not domain:
            raise ValueError("Domain is required: ICMD('icmd.questek.com')")

        self.domain = self._validate_domain(domain)
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

        # Connection pooling configuration
        adapter = HTTPAdapter(
            pool_connections=self._DEFAULT_POOL_CONNECTIONS,
            pool_maxsize=self._DEFAULT_POOL_MAXSIZE,
            max_retries=self._DEFAULT_MAX_RETRIES,
            pool_block=False,
        )
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        # Set reasonable timeouts by default
        self._default_timeout = self._DEFAULT_TIMEOUT

        # Cache for server config (reduces redundant HTTP requests)
        self._server_config_cache = None

        self._credentials = CredentialManager()

        # Clear cached credentials if requested
        if clear_cache:
            self._credentials.clear_domain_credentials(self.domain)

        # Handle developer token authentication (non-interactive)
        if developer_token:
            self._session.headers["Authorization"] = f"Bearer {developer_token}"
            self._developer_token = developer_token
            # Don't fail ICMD initialization if slim package management fails
            with contextlib.suppress(Exception):
                ensure_slim_packages(self)
            return

        self._developer_token = None

        # Validate and set auth method
        if auth_method:
            if auth_method.upper() not in ("SAML", "PASSWORD"):
                raise ValueError(
                    f"Invalid auth_method: {auth_method}. Must be 'SAML' or 'PASSWORD'"
                )
            self.auth_method = auth_method.upper()
        else:
            self.auth_method = self._auto_detect_auth_method()

        self._refresh_token = ""
        self._access_token = ""
        self._access_token_expiration = datetime.now(UTC)
        self._token_expire_buffer = timedelta(milliseconds=self._TOKEN_EXPIRE_BUFFER_MS)

        # Initialize default timeout (needed for tests that bypass __init__)
        if not hasattr(self, "_default_timeout"):
            self._default_timeout = self._DEFAULT_TIMEOUT

        # Display banner message if available (before auth prompts)
        self._display_banner_message()

        self._load_cached_credentials()

        if not skip_auth:
            self._ensure_authenticated()

            # Don't fail ICMD initialization if slim package management fails
            with contextlib.suppress(Exception):
                ensure_slim_packages(self)

    def _validate_domain(self, domain: str) -> str:
        """Validate domain format and return normalized domain.

        Args
        ----
            domain: Domain to validate

        Returns
        -------
            Normalized domain string

        Raises
        ------
            ValueError: If domain format is invalid
        """
        if not domain or not isinstance(domain, str):
            raise ValueError(f"Invalid domain: {domain}. Must be a non-empty string.")

        normalized = self._normalize_domain(domain)

        # Accept localhost for local development
        # Check both the original domain and the normalized one
        domain_to_check = domain.replace("http://", "").replace("https://", "")
        if self._is_local_domain(domain_to_check):
            return normalized

        # Accept: icmd.questek.com or *.icmd.questek.com
        if ".questek.com" in normalized:
            return normalized

        raise ValueError(
            f"Invalid domain: {domain}. "
            "Must be a 'questek.com' subdomain or localhost for development"
        )

    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain with appropriate protocol.

        Uses http:// for localhost, https:// otherwise.
        """
        if not isinstance(domain, str):
            raise ICMDValidationError("Domain must be a string")

        domain = domain.strip()
        if not domain:
            raise ICMDValidationError("Domain cannot be empty")

        if not domain.startswith("http"):
            # Use http:// for localhost/local development, https:// for production
            protocol = "http" if self._is_local_domain(domain) else "https"
            domain = f"{protocol}://{domain}"
        return domain

    def _is_local_domain(self, domain: str) -> bool:
        """Check if domain is a local development domain.

        Args
        ----
            domain: Domain string to check (without protocol)

        Returns
        -------
            True if domain is localhost, 127.0.0.1, or similar local patterns
        """
        domain_lower = domain.lower()
        # Check for localhost and local IP addresses
        return domain_lower.startswith(("localhost", "127.", "0.0.0.0", "[::1]"))

    def _display_banner_message(self) -> None:
        """Display banner message from server config if available."""
        try:
            config = self._get_server_config()
            banner_message = config.get("BANNER_MESSAGE", "").strip()

            if banner_message:
                # Display banner in a noticeable format with colored border
                border = "=" * 70
                print(f"\n\033[96m{border}\033[0m")
                print(f"\033[96m{banner_message}\033[0m")
                print(f"\033[96m{border}\033[0m\n")
        except Exception:
            # Silently fail if banner retrieval fails
            pass

    def _get_server_config(self) -> dict:
        """Fetch server configuration from /api/v1/public/config/ endpoint.

        Results are cached per instance to avoid redundant HTTP requests during initialization.
        Empty configs are not cached to allow retry.
        """
        # Return cached config if available and non-empty
        if self._server_config_cache:
            return self._server_config_cache

        try:
            config_url = f"{self.api_root}/public/config/"
            response = self._session.get(config_url, timeout=5)

            if response.status_code == HTTPStatus.OK:
                config = response.json()
                # Only cache non-empty successful responses
                if config:
                    self._server_config_cache = config
                return config
        except (requests.RequestException, ValueError, OSError, Exception):
            # Network issues, JSON parsing errors, timeouts, or any other errors
            pass

        # Don't cache failures or empty responses - allow retry on next call
        return {}

    def _enhance_auth_error(self, error_response: requests.Response, auth_method: str) -> str:
        """Enhance authentication error messages with Django-specific context."""
        base_error = f"{auth_method} authentication failed"
        enhanced_error = base_error

        try:
            error_data = error_response.json()
            if not isinstance(error_data, dict):
                return enhanced_error

            # Extract error details from Django response
            error = error_data.get("error", {})
            if isinstance(error, dict):
                error_code = error.get("code", "")
                error_msg = error.get("message", "")
            else:
                error_code = ""
                error_msg = error_data.get("message", "") or error_data.get("detail", "")

            # Map Django error codes to enhanced messages
            error_enhancements = {
                "invalid_credentials": "Invalid email or password",
                "account_inactive": "Account is inactive, contact administrator",
                "invalid_token": "Invalid or expired token",
                "invalid_code": "Invalid or expired MFA code",
                "mfa_required": "Multi-factor authentication required",
                "mfa_setup_required": (
                    "MFA not configured. Please configure MFA at "
                    f"https://{self.domain.replace('https://', '')}/account/security/"
                ),
                "rate_limit_exceeded": "Too many attempts, please wait before trying again",
            }

            # Check for specific error codes
            if error_code in error_enhancements:
                enhanced_error = f"{base_error}: {error_enhancements[error_code]}"
            # Handle networking errors
            elif "network" in error_msg.lower() or "timeout" in error_msg.lower():
                enhanced_error = f"{base_error}: Network connectivity issue"
            # Generic error message if available
            elif error_msg:
                enhanced_error = f"{base_error}: {error_msg}"

        except (ValueError, KeyError):
            pass

        return enhanced_error

    def _auto_detect_auth_method(self) -> str:
        """Enhanced auth method detection using server config discovery."""
        if cached := self._credentials.get_auth_method(self.domain):
            return cached

        # Server config discovery
        config = self._get_server_config()

        # Check Django AUTH_METHODS config
        if auth_methods := config.get("AUTH_METHODS", []):
            has_saml = any(method.get("type") == "saml" for method in auth_methods)
            has_password = any(method.get("type") == "password" for method in auth_methods)

            # If both methods available, let user choose
            if has_saml and has_password:
                return self._prompt_auth_method_selection()

            if has_saml:
                return "SAML"
            if has_password:
                return "PASSWORD"

        # Fallback: When server config is unavailable, default to PASSWORD
        return "PASSWORD"

    def _prompt_auth_method_selection(self) -> str:
        """Prompt user to select authentication method when multiple options available."""
        try:
            print("\n\033[94mMultiple authentication methods available:\033[0m")
            print("  [1] SAML SSO  [2] Password")

            while True:
                try:
                    choice = input("Select authentication method (1 or 2): ").strip()

                    if choice == "1":
                        return "SAML"
                    if choice == "2":
                        return "PASSWORD"
                    print("Invalid choice. Please enter 1 or 2.")
                except KeyboardInterrupt:
                    # Default to SAML on Ctrl+C
                    print("\nDefaulting to SAML SSO...")
                    return "SAML"
        except EOFError:
            # Non-interactive environment - default to SAML
            return "SAML"

    @property
    def api_root(self) -> str:
        """Return the root of the ICMD API."""
        return f"{self.domain}/api/v1"

    def _load_cached_credentials(self) -> None:
        """Load cached credentials from ~/.icmd.json."""
        if refresh_token := self._credentials.get_refresh_token(self.domain):
            self._refresh_token = refresh_token

    def _save_credentials(self) -> None:
        """Save credentials to ~/.icmd.json."""
        self._credentials.save_domain_credentials(
            self.domain, self.auth_method, self._refresh_token
        )

    def _is_token_expired(self) -> bool:
        """Check if current token is expired."""
        return self._access_token_expiration - self._token_expire_buffer <= datetime.now(UTC)

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid authentication token with smart refresh."""
        # Developer tokens bypass authentication flow
        if hasattr(self, "_developer_token") and self._developer_token:
            return

        # Check if we already have a valid token
        if self._access_token and not self._is_token_expired():
            return

        # Try refresh token if available
        if self._refresh_token:
            if self._refresh_access_token():
                return
            # Clear invalid refresh token from storage
            self._credentials.clear_refresh_token(self.domain)

        # Full authentication required
        self._perform_authentication()

    def authenticate(self) -> None:
        """Manually trigger authentication. Useful when ICMD was created with skip_auth=True."""
        self._ensure_authenticated()

        # Don't fail if slim package management fails
        with contextlib.suppress(Exception):
            ensure_slim_packages(self)

    def _refresh_access_token(self) -> bool:
        """Refresh access token using refresh token.

        Returns
        -------
            bool: True if refresh successful, False otherwise
        """
        try:
            url = f"{self.api_root}/account/auth/refresh/"
            response = self._session.post(
                url,
                json={"refresh_token": self._refresh_token},
                timeout=self._REFRESH_TIMEOUT,
            )

            if response.status_code != HTTPStatus.OK:
                # Clear tokens on failure
                self._access_token = ""
                self._refresh_token = ""
                self._session.headers.pop("Authorization", None)
                return False

            # Handle token rotation (new refresh_token in response)
            self._handle_auth_response(response)
            return True

        except (requests.RequestException, Exception):
            # Clear tokens on any error
            self._access_token = ""
            self._refresh_token = ""
            self._session.headers.pop("Authorization", None)
            return False

    def _perform_authentication(self) -> None:
        """Perform full authentication flow."""
        if self.auth_method == "SAML":
            self._saml_authentication()
        else:
            self._password_authentication()

        self._save_credentials()

    def _password_authentication(self) -> None:
        """Authenticate with email/password (Django JWT)."""
        try:
            email = input("Your ICMD® email: ").strip()
            if not email:
                raise ICMDValidationError("Email cannot be empty")

            password = getpass("Your ICMD® password: ")
            if not password:
                raise ICMDValidationError("Password cannot be empty")

            url = f"{self.api_root}/account/auth/login/"
            response = self._session.post(
                url,
                json={"email": email, "password": password},
                timeout=self._default_timeout,
            )

            if response.status_code != HTTPStatus.OK:
                error_msg = self._enhance_auth_error(response, "PASSWORD")
                raise ICMDAuthenticationError(error_msg)

            auth_data = response.json()

            # Check if MFA is required
            if auth_data.get("requires_mfa"):
                self._handle_mfa_challenge(auth_data)
            else:
                self._handle_auth_response(response)

        except EOFError:
            raise ICMDAuthenticationError(
                "Cannot authenticate in non-interactive environment. "
                "Consider using ICMD(skip_auth=True) and calling authenticate() later."
            ) from None
        except requests.RequestException as e:
            raise ICMDConnectionError(f"Network error during password authentication: {e}") from e
        except KeyboardInterrupt:
            raise ICMDAuthenticationError("Authentication cancelled by user") from None

    def _handle_mfa_challenge(self, mfa_response: dict) -> None:
        """Handle Django MFA challenge with retry logic."""
        try:
            # Extract session token and available methods
            session_token = mfa_response.get("session_token")
            available_methods = mfa_response.get("available_methods", [])

            if not session_token:
                raise ICMDAuthenticationError("Invalid MFA response: missing session token")

            # Detect MFA method
            if "totp" in available_methods:
                method = "totp"
                prompt = "Enter MFA code from authenticator app: "
            elif "email" in available_methods:
                method = "email"
                prompt = "MFA code sent to your email. Enter code: "
            else:
                method = available_methods[0] if available_methods else "totp"
                prompt = "Enter MFA code: "

            # Allow up to 3 attempts
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    mfa_code = input(prompt).strip()

                    if not mfa_code:
                        raise ICMDValidationError("MFA code cannot be empty")

                    url = f"{self.api_root}/account/auth/mfa/verify/"

                    # Set session token in Authorization header (not in body)
                    headers = {"Authorization": f"Session {session_token}"}

                    response = self._session.post(
                        url,
                        json={
                            "method": method,
                            "code": mfa_code,
                        },
                        headers=headers,
                        timeout=self._default_timeout,
                    )

                    if response.status_code == HTTPStatus.OK:
                        self._handle_auth_response(response)
                        return

                    # Handle error
                    error_data = response.json()
                    error = error_data.get("error", {})
                    error_code = error.get("code", "") if isinstance(error, dict) else ""

                    if error_code == "invalid_code" and attempt < max_attempts:
                        remaining = max_attempts - attempt
                        print(f"Invalid code. {remaining} attempt(s) remaining.")
                        continue
                    error_msg = self._enhance_auth_error(response, "MFA")
                    raise ICMDAuthenticationError(error_msg)

                except KeyboardInterrupt:
                    raise ICMDAuthenticationError("MFA verification cancelled by user") from None

            raise ICMDAuthenticationError("MFA verification failed: Maximum attempts exceeded")

        except requests.RequestException as e:
            raise ICMDConnectionError(f"Network error during MFA verification: {e}") from e

    def _get_saml_provider(self) -> dict:
        """Get SAML provider configuration from server.

        Returns
        -------
            dict: SAML provider info with 'id', 'name', and 'login_url'

        Raises
        ------
            ICMDAuthenticationError: If no SAML providers configured or selection fails
        """
        try:
            config = self._get_server_config()
            saml_providers = config.get("SAML_PROVIDERS", [])

            if not saml_providers:
                raise ICMDAuthenticationError(
                    "SAML authentication is not configured on this server. "
                    "Please contact your administrator or use password authentication."
                )

            # If only one provider, auto-select
            if len(saml_providers) == 1:
                provider = saml_providers[0]
                print(f"Using SAML provider: {provider.get('name', provider['id'])}")
                return provider

            # Multiple providers - let user choose
            print("\n\033[94mMultiple SAML providers available:\033[0m")
            for idx, provider in enumerate(saml_providers, 1):
                provider_name = provider.get("name", provider["id"])
                description = provider.get("description", "")
                if description:
                    print(f"  [{idx}] {provider_name} - {description}")
                else:
                    print(f"  [{idx}] {provider_name}")

            n_providers = len(saml_providers)
            while True:
                try:
                    choice = input(f"\nSelect SAML provider (1-{n_providers}): ").strip()

                    try:
                        choice_idx = int(choice) - 1
                        if 0 <= choice_idx < n_providers:
                            return saml_providers[choice_idx]
                        print(
                            f"Invalid choice. Please enter a number between 1 and {n_providers}."
                        )
                    except ValueError:
                        print(f"Invalid input. Please enter a number between 1 and {n_providers}.")

                except KeyboardInterrupt:
                    # Default to first provider on Ctrl+C
                    print(
                        f"\nDefaulting to {
                            saml_providers[0].get('name', saml_providers[0]['id'])
                        }..."
                    )
                    return saml_providers[0]

        except EOFError:
            # Non-interactive environment - use first provider
            if saml_providers:
                return saml_providers[0]
            raise ICMDAuthenticationError(
                "Cannot select SAML provider in non-interactive environment"
            ) from None

    def _saml_authentication(self) -> None:
        """Authenticate with Django SAML SSO."""
        try:
            from urllib.parse import quote

            # Get SAML provider configuration
            provider = self._get_saml_provider()

            # Use provider's login URL with SDK flag in relay_state
            relay_state = quote("/auth/callback?sdk=true")
            consent_url = f"{self.domain}{provider['login_url']}&relay_state={relay_state}"

            # Display the authentication link
            print(f"\n\033[94mSAML SSO Authentication Link:\033[0m\n{consent_url}")

            # Compact messaging for Jupyter notebooks
            print("\n\033[94mOpening browser...\033[0m Copy the auth code (5 min expiry)")

            # Attempt to open browser automatically
            with contextlib.suppress(Exception):
                webbrowser.open(consent_url)

            # Compact input prompt
            auth_code = input("Auth Code: ").strip()
            if not auth_code:
                raise ICMDValidationError("Authentication code required")

            # Exchange auth code for tokens
            url = f"{self.api_root}/account/auth/login/"
            response = self._session.post(
                url,
                json={"auth_code": auth_code},
                timeout=self._default_timeout,
            )

            if response.status_code != HTTPStatus.OK:
                error_msg = self._enhance_auth_error(response, "SAML")
                raise ICMDAuthenticationError(error_msg)

            self._handle_auth_response(response)
            print("\033[92m✓ Authenticated\033[0m")

        except requests.RequestException as e:
            raise ICMDConnectionError(f"Network error during SAML authentication: {e}") from e
        except KeyboardInterrupt:
            raise ICMDAuthenticationError("SAML authentication cancelled by user") from None

    def _handle_auth_response(self, response: requests.Response) -> None:
        """Handle Django JWT authentication response and extract tokens."""
        auth_data = response.json()

        # Check for error response
        if not auth_data.get("success", False):
            error = auth_data.get("error", {})
            error_msg = error.get("message", "Authentication failed")
            raise ICMDAuthenticationError(error_msg)

        # Update session headers with user UUID
        if (user_data := auth_data.get("user")) and (user_uuid := user_data.get("uuid")):
            self._session.headers["X-User-Context"] = user_uuid

        # Extract tokens
        self._access_token = auth_data.get("access_token", "")
        if refresh_token := auth_data.get("refresh_token"):
            self._refresh_token = refresh_token

        # Calculate expiration from expires_in (seconds)
        if expires_in := auth_data.get("expires_in"):
            self._access_token_expiration = datetime.now(UTC) + timedelta(seconds=expires_in)

        # Set bearer auth
        if self._access_token:
            self._session.headers["Authorization"] = f"Bearer {self._access_token}"

        # Handle cookies
        for cookie in response.cookies:
            if cookie.name == "Secure-Fgp" and cookie.value:
                self._session.cookies.set("Secure-Fgp", cookie.value)

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request to ICMD API with smart retry and error handling."""
        try:
            self._ensure_authenticated()

            # Clean and validate endpoint
            if not endpoint:
                raise ICMDValidationError("Endpoint cannot be empty")

            endpoint = endpoint.strip("/")
            url = f"{self.api_root}/{endpoint}/"

            # Set default timeout if not provided
            if "timeout" not in kwargs:
                kwargs["timeout"] = self._default_timeout

            # Make request with automatic retry on auth failure
            response = self._session.request(method, url, **kwargs)

            # Handle token expiration with single retry
            if response.status_code == HTTPStatus.UNAUTHORIZED and not kwargs.get(
                "_retry_attempted"
            ):
                # Check if endpoint is excluded from auto-refresh
                if endpoint in self.EXCLUDED_ENDPOINTS:
                    return response

                # Check error detail for selective logout
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "").lower()
                    # Only auto-refresh for specific token-related errors
                    if any(
                        msg in error_detail
                        for msg in ["invalid token", "token has expired", "not authenticated"]
                    ):
                        # Set retry flag to prevent infinite loop
                        kwargs["_retry_attempted"] = True

                        # Attempt token refresh
                        if self._refresh_access_token():
                            # Retry with refreshed token
                            response = self._session.request(method, url, **kwargs)
                        else:
                            # Refresh failed, return original 401 response
                            return response
                except (ValueError, KeyError):
                    # If response is not JSON or doesn't have expected structure, don't retry
                    pass

            return response

        except (ICMDAuthenticationError, ICMDConnectionError, ICMDValidationError):
            # Re-raise our custom exceptions
            raise
        except requests.RequestException as e:
            raise ICMDConnectionError(f"Request failed for {method} {endpoint}: {e}") from e
        except Exception as e:
            raise ICMDConnectionError(f"Unexpected error during request: {e}") from e

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """GET request."""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, data: Any = None, **kwargs) -> requests.Response:
        """POST request."""
        return self.request("POST", endpoint, json=data, **kwargs)

    def put(self, endpoint: str, data: Any = None, **kwargs) -> requests.Response:
        """PUT request."""
        return self.request("PUT", endpoint, json=data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """DELETE request."""
        return self.request("DELETE", endpoint, **kwargs)

    def logout(self, clear_saved_credentials: bool = False) -> None:
        """Logout and clear session.

        Args:
            clear_saved_credentials: If True, also clear cached credentials from disk.
                                   Default False (preserves refresh token for faster re-auth).
        """
        # Best effort logout call to server (ignore errors)
        try:
            if self._access_token:
                url = f"{self.api_root}/account/auth/logout/"
                self._session.post(url, timeout=5)
        except Exception:
            pass  # Ignore errors, proceed with local cleanup

        # Clear in-memory tokens
        self._access_token = ""
        self._refresh_token = ""
        self._access_token_expiration = datetime.now(UTC)

        # Remove Authorization header
        self._session.headers.pop("Authorization", None)

        # Optionally clear saved credentials
        if clear_saved_credentials:
            self._credentials.clear_refresh_token(self.domain)

        print("Logged out successfully.")
