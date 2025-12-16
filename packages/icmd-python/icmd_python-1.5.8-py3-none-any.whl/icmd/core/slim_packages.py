"""Slim package management for icmd-python.

This module handles downloading and injecting slim versions of qt-models and qt-calphad
packages at runtime. The packages are downloaded from the backend after authentication
and injected into sys.path for seamless import.
"""

import importlib.util
import json
import shutil
import sys
import tempfile
import zipfile
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from .client import ICMD

# Base directory for all slim packages
QTPY_SLIM_BASE = Path.home() / ".icmd" / "qtpy_slim"

# Backend endpoint (authenticated) - returns both version and download URL
SLIM_PACKAGES_ENDPOINT = "core/slim-packages/"

# Packages to check
MANAGED_PACKAGES = ["qt_models", "qt_calphad", "qt_base", "qt_optimizer", "qt_designer"]


def get_server_slug(domain: str) -> str:
    """Convert server domain to filesystem-safe directory name.

    Parameters
    ----------
    domain : str
        Server domain (e.g., "https://icmd.questek.com")

    Returns
    -------
    str
        Filesystem-safe slug (e.g., "icmd.questek.com")
    """
    # Remove protocol and trailing slashes, then replace any remaining slashes with underscores
    return domain.replace("https://", "").replace("http://", "").strip("/").replace("/", "_")


def check_package_availability() -> dict[str, bool]:
    """Check if qt_models/qt_calphad are already available in sys.path.

    This checks if packages are installed by user (e.g., via pip install in dev environment).
    Does NOT check ~/.icmd/slim_packages since we haven't injected it yet.

    Returns
    -------
    dict[str, bool]
        Dictionary mapping package names to availability status
        Example: {"qt_models": True, "qt_calphad": False}
    """
    availability = {}
    for package_name in MANAGED_PACKAGES:
        spec = importlib.util.find_spec(package_name)
        availability[package_name] = spec is not None
    return availability


def get_local_version(server_dir: Path) -> dict | None:
    """Get the locally installed slim packages version for a server.

    Parameters
    ----------
    server_dir : Path
        Server-specific directory containing versions.json

    Returns
    -------
    dict | None
        Version data with repo commit SHAs, or None if not installed
    """
    version_file = server_dir / "versions.json"

    if not version_file.exists():
        return None

    try:
        return json.loads(version_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def get_slim_packages_info(icmd_client: "ICMD") -> tuple[dict | None, str | None]:
    """Get slim packages info from backend (version metadata + download URL).

    This function calls the unified /slim-packages/ endpoint that returns both
    version metadata and a download URL in a single response, avoiding duplicate
    API calls.

    Parameters
    ----------
    icmd_client : ICMD
        Authenticated ICMD client instance

    Returns
    -------
    tuple[dict | None, str | None]
        (version_data, download_url) tuple where:
        - version_data: Dict with package versions and content_hash, or None if unavailable
        - download_url: URL to download qtpy_slim.zip (signed S3 or local), or None if unavailable
    """
    try:
        response = icmd_client.get(SLIM_PACKAGES_ENDPOINT, timeout=5)
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            version_data = data.get("version")
            download_url = data.get("qtpy_slim_url")
            return version_data, download_url
        # Non-200 response
        print(
            f"⚠ Warning: Slim packages endpoint returned status {response.status_code}. "
            f"Using cached version if available."
        )
        return None, None
    except requests.Timeout:
        print(
            "⚠ Warning: Timeout checking slim packages version from backend (5s timeout). "
            "Using cached version if available."
        )
        return None, None
    except requests.RequestException as e:
        print(
            f"⚠ Warning: Network error checking slim packages version: {type(e).__name__}. "
            "Using cached version if available."
        )
        return None, None
    except Exception as e:
        print(
            f"⚠ Warning: Error checking slim packages version: {type(e).__name__}: {e}. "
            "Using cached version if available."
        )
        return None, None


def versions_match(local: dict | None, remote: dict | None) -> bool:
    """Compare package versions robustly by individual version strings.

    This avoids fragile dict equality comparison that breaks when
    metadata fields differ (created_at, content_hash, etc.).

    Parameters
    ----------
    local : dict | None
        Local version data
    remote : dict | None
        Remote version data

    Returns
    -------
    bool
        True if all managed package versions match, False otherwise
    """
    if local is None or remote is None:
        return False

    # Compare each managed package version string
    for package in MANAGED_PACKAGES:
        repo_name = package.replace("_", "-")  # qt_models -> qt-models

        local_ver = local.get(repo_name, "unknown")
        remote_ver = remote.get(repo_name, "unknown")

        if local_ver != remote_ver:
            return False

    return True


def should_download(local_version: dict | None, remote_version: dict | None) -> bool:
    """Determine if download is needed based on content hash or version strings.

    Priority:
    1. Content hash comparison (most accurate) - if available on both
    2. Individual package version comparison (robust fallback)
    3. Default to download if uncertain

    Parameters
    ----------
    local_version : dict | None
        Local version data
    remote_version : dict | None
        Remote version data

    Returns
    -------
    bool
        True if download is needed, False if local version is sufficient
    """
    if remote_version is None:
        return False  # Can't download without remote info

    if local_version is None:
        return True  # No local version, must download

    # PRIMARY CHECK: Content hash (if available on both)
    local_hash = local_version.get("content_hash")
    remote_hash = remote_version.get("content_hash")

    if local_hash and remote_hash:
        # Content hash available - use it for accurate comparison
        return local_hash != remote_hash

    # FALLBACK: Compare individual package versions
    # (for backward compat or when hash unavailable)
    return not versions_match(local_version, remote_version)


def download_and_extract(download_url: str, dest_path: Path) -> bool:
    """Download and extract slim packages zip file atomically.

    Uses temporary directory for download/extraction, then atomically moves
    to final destination. This ensures old packages remain intact if download
    or extraction fails, and temporary files are always cleaned up.

    Parameters
    ----------
    download_url : str
        Full URL to download qtpy_slim.zip from (signed S3 URL or authenticated media path)
    dest_path : Path
        Destination directory for extracted packages

    Returns
    -------
    bool
        True if download and extraction successful, False otherwise
    """
    try:
        # Download zip file from provided URL
        # For S3: URL is pre-signed and needs no additional auth
        # For local: URL is relative path that needs session auth
        response = requests.get(download_url, timeout=30)
        if response.status_code != HTTPStatus.OK:
            print(
                f"⚠ Warning: Failed to download slim packages "
                f"(HTTP {response.status_code}: {response.reason})"
            )
            return False

        # Use temporary directory for download/extraction (auto-cleanup)
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_dir = Path(tmpdir)

            # Save zip file to temp directory
            zip_path = temp_dir / "qtpy_slim.zip"
            zip_path.write_bytes(response.content)

            # Extract to temp directory
            extract_dir = temp_dir / "extracted"
            extract_dir.mkdir()
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            # Verify extraction (check for versions.json)
            if not (extract_dir / "versions.json").exists():
                print("⚠ Warning: Extracted packages missing versions.json")
                return False

            # Atomic move to final location
            # Remove old version if exists, then move new version
            if dest_path.exists():
                shutil.rmtree(dest_path)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(extract_dir), str(dest_path))

            return True

    except Exception as e:
        print(f"⚠ Warning: Failed to download/extract slim packages: {e}")
        return False


def inject_slim_packages_path(server_dir: Path) -> None:
    """Inject server-specific slim packages directory into sys.path.

    This allows importing qt_models and qt_calphad packages seamlessly.
    User-installed full versions take precedence (earlier in sys.path).

    Parameters
    ----------
    server_dir : Path
        Server-specific qtpy_slim directory to inject
    """
    if not server_dir.exists():
        return

    # Remove any existing qtpy_slim paths from sys.path to prevent conflicts
    # This handles cases where old global path or different server paths exist
    qtpy_slim_base_str = str(QTPY_SLIM_BASE)
    sys.path[:] = [p for p in sys.path if not p.startswith(qtpy_slim_base_str)]

    # Add new server-specific path
    slim_packages_path = str(server_dir)
    if slim_packages_path not in sys.path:
        sys.path.append(slim_packages_path)


def _format_version_info(version_data: dict | None) -> str:
    """Format version data for display.

    Parameters
    ----------
    version_data : dict | None
        Version dictionary with package versions

    Returns
    -------
    str
        Formatted version string
    """
    if not version_data:
        return "unknown"

    parts = []
    for repo in ["qt-models", "qt-calphad", "qt-base", "qt-optimizer"]:
        if repo in version_data and version_data[repo] != "unknown":
            version = version_data[repo]
            parts.append(f"{repo}@{version}")
    return ", ".join(parts) if parts else "unknown"


def ensure_slim_packages(icmd_client: "ICMD") -> None:
    """Ensure slim packages are available, download if needed.

    This function is called after authentication to check if slim packages
    need to be downloaded or updated. Implements session-aware version tracking
    to prevent conflicting package versions within the same Python session.

    Logic:
    1. Check session state - if qtpy already loaded, verify compatibility
    2. Check if packages already available in sys.path (user installed)
    3. If available: Only check version and warn if mismatch
    4. If not available: Download/inject slim packages for this server
    5. Track loaded version in ICMD class variables

    Parameters
    ----------
    icmd_client : ICMD
        Authenticated ICMD client instance
    """
    try:
        # Import here to avoid circular dependency at module level
        from .client import ICMD

        # Get remote version and download URL from backend (single API call)
        remote_version, download_url = get_slim_packages_info(icmd_client)
        if remote_version is None:
            # Backend unavailable - print warning and try cached version
            print(
                "⚠ Warning: Could not check slim packages version from backend. "
                "Using cached version if available."
            )
            # Try to inject cached version for this server
            server_dir = QTPY_SLIM_BASE / get_server_slug(icmd_client.domain)
            if server_dir.exists():
                inject_slim_packages_path(server_dir)
            return

        # SESSION CONFLICT CHECK: Ensure no conflicting version already loaded
        if ICMD._session_qtpy_version is not None:
            # Check if versions differ (using content hash if available, else version strings)
            if should_download(ICMD._session_qtpy_version, remote_version):
                # Version conflict - warn user
                current_server_slug = (
                    get_server_slug(ICMD._session_qtpy_server)
                    if ICMD._session_qtpy_server
                    else "unknown"
                )
                requested_server_slug = get_server_slug(icmd_client.domain)
                current_version_str = _format_version_info(ICMD._session_qtpy_version)
                requested_version_str = _format_version_info(remote_version)

                print("\n⚠ Warning: qtpy version conflict detected in this Python session:")
                print(f"  • Current session: {current_server_slug} ({current_version_str})")
                print(f"  • Requested: {requested_server_slug} ({requested_version_str})")
                print("  → Using existing session version. Restart Python to switch servers.")
                return

            # Same version already loaded - nothing to do
            return

        # First, check if packages are already available (user installed via pip)
        availability = check_package_availability()
        packages_available = any(availability.values())

        if packages_available:
            # User has packages installed, only check version and warn
            available_packages = [pkg for pkg, avail in availability.items() if avail]
            installed = ", ".join(available_packages)

            # Track this as the session version
            ICMD._session_qtpy_version = remote_version
            ICMD._session_qtpy_server = icmd_client.domain
            ICMD._session_qtpy_path = None  # User installed, not from our cache

            backend_version = _format_version_info(remote_version)
            print(
                f"⚠ Warning: Using locally installed packages ({installed}). "
                f"Backend version: {backend_version}"
            )
            return

        # No packages available from user environment, proceed with slim packages
        server_dir = QTPY_SLIM_BASE / get_server_slug(icmd_client.domain)
        local_version = get_local_version(server_dir)

        # Download if needed (based on content hash or version strings)
        if should_download(local_version, remote_version):
            if download_url:
                print(f"Downloading slim packages: {_format_version_info(remote_version)}...")
                if download_and_extract(download_url, server_dir):
                    print("✓ Slim packages downloaded successfully")
                else:
                    print(
                        "⚠ Warning: Failed to download slim packages. "
                        "Using cached version if available."
                    )
            else:
                print("⚠ Warning: Download URL not available from backend")

        # Inject server-specific slim packages path
        inject_slim_packages_path(server_dir)

        # Track this as the session version
        ICMD._session_qtpy_version = remote_version
        ICMD._session_qtpy_server = icmd_client.domain
        ICMD._session_qtpy_path = server_dir

    except Exception as e:
        # Don't fail ICMD initialization if slim package management fails
        print(f"⚠ Warning: Error managing slim packages: {e}")
        # Try to inject cached version for this server if it exists
        server_dir = QTPY_SLIM_BASE / get_server_slug(icmd_client.domain)
        if server_dir.exists():
            inject_slim_packages_path(server_dir)
