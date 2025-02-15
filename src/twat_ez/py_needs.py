#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "fire",
# ]
# ///
# this_file: py_needs.py

"""
A focused module that provides QtNetwork-based download functionality with
a synchronous Python interface. Handles HTTP redirects automatically.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import platform
import shutil
import site
import subprocess
import sys
from collections.abc import Callable
from functools import lru_cache, wraps
from pathlib import Path

###############################
## PATH PROVIDERS & ENVIRONMENT FUNCTIONS
###############################
"""
Functions related to system path management including:
- Custom path provider registration
- System-specific path discovery
- PATH environment manipulation
"""


# Type for path provider functions
PathProvider = Callable[[], list[str]]

# Registry for custom path providers
_path_providers: list[PathProvider] = []

# Configure basic logging
logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)s: %(message)s", stream=sys.stdout
)


def _get_fontlab_site_packages() -> Path | None:
    """
    Get the FontLab site-packages directory path if FontLab is available.

    This function attempts to locate the FontLab-specific site-packages directory
    by using FontLab's data path and the current Python version. This is needed
    because FontLab maintains its own Python environment.

    Returns:
        Path: Path to FontLab's site-packages directory if found and in sys.path
        None: If FontLab is not available or the path is not in sys.path
    """
    try:
        import fontlab

        # Get FontLab data path
        fontlab_path = Path(fontlab.flPreferences.instance().dataPath)

        # Get current Python version (major.minor)
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

        # Construct the full path
        site_packages_path = fontlab_path / "python" / python_version / "site-packages"

        # Only return the path if it's actually in sys.path
        return site_packages_path if str(site_packages_path) in sys.path else None

    except ImportError:
        return None


def get_site_packages_path() -> Path:
    # Get FontLab site-packages if available, otherwise fall back to user site-packages
    return _get_fontlab_site_packages() or Path(site.getusersitepackages())


####################################
## INSTALLATION TARGET CONFIG
####################################
# Configurable via UV_INSTALL_TARGET environment variable
UV_INSTALL_TARGET = Path(
    os.environ.get(
        "UV_INSTALL_TARGET",
        str(get_site_packages_path()),
    )
)


def register_path_provider(provider: PathProvider) -> None:
    """Register a custom path provider function."""
    _path_providers.append(provider)
    clear_path_cache()  # Invalidate cache when providers change


####################################
## XDG PATH MANAGEMENT
####################################
def get_xdg_paths() -> list[Path]:
    """
    Get XDG specification paths for common tool installations.

    Returns:
        list[Path]: List of XDG paths where executables may be found
    """
    paths: list[Path] = []

    # XDG_BIN_HOME
    if xdg_bin := os.environ.get("XDG_BIN_HOME"):
        paths.append(Path(xdg_bin))

    # XDG_DATA_HOME/../bin
    if xdg_data := os.environ.get("XDG_DATA_HOME"):
        data_parent_bin = Path(xdg_data).parent / "bin"
        paths.append(data_parent_bin)

    # Default ~/.local/bin if XDG vars not set
    local_bin = Path.home() / ".local" / "bin"
    if local_bin.exists() and local_bin not in paths:
        paths.append(local_bin)

    return paths


####################################
## SYSTEM-SPECIFIC PATH DISCOVERY
####################################
def get_system_specific_paths() -> list[Path]:
    """
    Get OS-specific executable paths.

    Returns:
        list[Path]: List of system-specific paths where executables may be found
    """
    system = platform.system()
    paths: list[Path] = []

    if system == "Darwin":  # macOS
        paths.extend(
            [
                Path("/usr/local/bin"),  # Homebrew (Intel)
                Path("/usr/local/sbin"),
                Path("/opt/homebrew/bin"),  # Homebrew (Apple Silicon)
                Path("/opt/homebrew/sbin"),
                Path("/usr/bin"),
                Path("/usr/sbin"),
                Path("/bin"),
                Path("/sbin"),
                Path("/Library/Apple/usr/bin"),
                Path("/Applications/Xcode.app/Contents/Developer/usr/bin"),
            ]
        )
    elif system == "Windows":
        win_dir = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        paths.extend(
            [
                Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps",
                win_dir / "System32",
                win_dir,
                win_dir / "System32" / "Wbem",
                win_dir / "System32" / "WindowsPowerShell" / "v1.0",
                Path(r"C:\Program Files\PowerShell\7"),
                Path(r"C:\ProgramData\chocolatey\bin"),
            ]
        )
    else:  # Linux and others
        paths.extend(
            [
                Path("/usr/local/bin"),
                Path("/usr/local/sbin"),
                Path("/usr/bin"),
                Path("/usr/sbin"),
                Path("/bin"),
                Path("/sbin"),
            ]
        )

        # Add snap paths if they exist
        snap_bin = Path("/snap/bin")
        if snap_bin.exists():
            paths.append(snap_bin)

    return paths


###############################
## UTILITY FUNCTIONS
###############################
"""
Core utilities for system interaction including:
- Executable verification
- Enhanced which implementation
- Data type conversion
"""


####################################
## EXECUTABLE SECURITY
####################################
def verify_executable(path: str | Path) -> tuple[bool, str]:
    """
    Validate executable safety and permissions.

    Args:
        path: Path to the executable as string or Path object

    Returns:
        tuple[bool, str]: (is_safe, reason) where is_safe is True if executable is safe to use
    """
    path_obj = Path(path)

    if not path_obj.exists():
        return False, "File does not exist"

    if not path_obj.is_file():
        return False, "Not a regular file"

    # Check if path is writable by others on Unix-like systems
    if platform.system() != "Windows":
        mode = path_obj.stat().st_mode
        if mode & 0o002:  # World-writable
            return False, "File is world-writable"

    # On Windows, we could add additional checks like:
    # - Digital signature verification
    # - Known paths validation
    # But for now we'll keep it simple

    return True, "OK"


####################################
## DATA CONVERSION
####################################
def bin_or_str(data: bytes, mode: int = 0) -> bytes | str:
    """Convert bytes to string based on decoding mode."""
    match mode:
        case 1:
            try:
                return data.decode("utf-8")
            except UnicodeDecodeError:
                return data
        case 2:
            return data.decode("utf-8")
        case _:
            return data


###############################
## URL DOWNLOAD FUNCTIONS
###############################
"""
Network utilities for HTTP content retrieval with:
- QtNetwork implementation (priority)
- urllib fallback implementation
"""


####################################
## CORE DOWNLOAD MECHANISMS
####################################
@lru_cache(maxsize=20)
def download_url_qt(
    url: str,
    mode: int = 1,
    max_redir: int = 5,
) -> bytes | str:
    """
    Fetch URL with redirect handling. Returns bytes/str based on mode.

    Args:
        url: HTTP/HTTPS URL to download from
        max_redir: Maximum number of redirects to follow (default: 5)
        mode: 0 for raw bytes, 1 for string or bytes, 2 for string

    Returns:
        bytes | str: Downloaded content

    Raises:
        RuntimeError: For network errors, too many redirects, or invalid responses
    """
    from PythonQt import QtNetwork
    from PythonQt.QtCore import QEventLoop, QUrl

    loop, nam = QEventLoop(), QtNetwork.QNetworkAccessManager()
    current_url, redir_count = QUrl(url), 0

    while redir_count <= max_redir:
        reply = nam.get(QtNetwork.QNetworkRequest(current_url))
        reply.finished.connect(loop.quit)
        loop.exec_()

        if (
            sc := reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
        ) in {301, 302, 303, 307, 308}:
            if (
                redir_url := reply.attribute(
                    QtNetwork.QNetworkRequest.RedirectionTargetAttribute
                )
            ).isValid():
                current_url, redir_count = (
                    reply.url().resolved(redir_url),
                    redir_count + 1,
                )
                reply.deleteLater()
                continue
            reply.deleteLater()
            msg = f"Invalid redirect (HTTP {sc})"
            raise RuntimeError(msg)

        if reply.error() == QtNetwork.QNetworkReply.NoError:
            data = bin_or_str(reply.readAll().data(), mode)
            reply.deleteLater()
            return data

        err = f"{reply.errorString()} (HTTP {sc})"
        reply.deleteLater()
        msg = f"Download failed: {err}"
        raise RuntimeError(msg)

    msg = f"Max redirects exceeded ({max_redir})"
    raise RuntimeError(msg)


@lru_cache(maxsize=20)
def download_url_py(
    url: str,
    mode: int = 1,
    max_redir: int = 5,
) -> bytes | str:
    """
    Fetch URL with redirect handling using urllib. Returns bytes/str based on mode.

    Args:
        url: HTTP/HTTPS URL to download from
        max_redir: Maximum number of redirects to follow (default: 5)
        mode: 0 for raw bytes, 1 for string or bytes, 2 for string

    Returns:
        bytes | str: Downloaded content

    Raises:
        RuntimeError: For network errors, too many redirects, or invalid responses
    """
    import urllib.error
    import urllib.request

    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "Python-urllib/3.x")]

    try:
        with opener.open(url) as response:
            data = response.read()
            return bin_or_str(data, mode)
    except urllib.error.HTTPError as e:
        msg = f"Download failed: HTTP {e.code} - {e.reason}"
        raise RuntimeError(msg)
    except urllib.error.URLError as e:
        msg = f"Download failed: {e.reason!s}"
        raise RuntimeError(msg)
    except Exception as e:
        msg = f"Download failed: {e!s}"
        raise RuntimeError(msg)


@lru_cache(maxsize=20)
def download_url(
    url: str,
    mode: int = 1,
    max_redir: int = 5,
) -> bytes | str:
    try:
        return download_url_qt(url, mode, max_redir)
    except Exception:
        return download_url_py(url, mode, max_redir)


###############################
## UV INSTALLATION HELPERS
###############################
"""
UV package manager lifecycle management:
- Installation routines
- Binary location
- Dependency verification
"""


####################################
## UV MANAGEMENT
####################################
@lru_cache(maxsize=20)
def which_uv() -> Path | None:
    """
    Locate the uv executable in the system path.

    Returns:
        Path | None: Path to uv executable if found, None otherwise
    """
    try:
        uv_cli = which("uv")
        if uv_cli:
            return uv_cli
    except Exception as e:
        logging.warning(f"Error finding uv: {e!s}")
        return None

    # If uv is not found, try to install it using pip
    pip_cli = which_pip()
    if pip_cli:
        try:
            subprocess.run(
                [str(pip_cli), "install", "--user", "uv"],
                check=True,
                capture_output=True,
            )
            # Try finding uv again after installation
            uv_cli = which("uv")
            if uv_cli:
                return uv_cli
        except subprocess.CalledProcessError as e:
            logging.warning(f"Error installing uv: {e!s}")
        except Exception as e:
            logging.warning(f"Unexpected error installing uv: {e!s}")

    return None


####################################
## PIP MANAGEMENT
####################################
@lru_cache(maxsize=20)
def which_pip() -> Path | None:
    try:
        pip_cli = which("pip")
        if pip_cli:
            pip_cli = Path(pip_cli)
            if pip_cli.exists():
                return pip_cli
    except ImportError:
        pass

    try:
        pip_cli = which("pip")
        if pip_cli:
            pip_cli = Path(pip_cli)
            if pip_cli.exists():
                return pip_cli
    except Exception:
        pass
    try:
        import ensurepip

        ensurepip.bootstrap()
        importlib.import_module("pip")
        pip_cli = which("pip")
        if pip_cli:
            pip_cli = Path(pip_cli)
            if pip_cli.exists():
                return pip_cli
    except Exception as e:
        logging.warning(f"Error ensuring pip: {e!s}")
    return None


####################################
## EXECUTABLE SECURITY
####################################
@lru_cache(maxsize=20)
def which(
    cmd: str,
    mode: int = os.F_OK | os.X_OK,
    path: str | None = None,
    verify: bool = True,
) -> Path | None:
    """
    Enhanced version of shutil.which that searches an extended set of paths.

    Args:
        cmd: The command to search for
        mode: The mode to use when checking if a file is executable
        path: Optional path string to use instead of building one
        verify: Whether to perform security verification

    Returns:
        Path | None: Full path to the command if found, None otherwise
    """
    if path is None:
        path = build_extended_path()

    if result := shutil.which(cmd, mode=mode, path=path):
        result_path = Path(result)

        if verify:
            is_safe, reason = verify_executable(result_path)
            if not is_safe:
                if os.environ.get("CLIFIND_DEBUG"):
                    pass
                return None

        if result_path.exists():
            return result_path

    return None


@lru_cache(maxsize=20)
def build_extended_path() -> str:
    """
    Build a comprehensive PATH string combining:
    1. Current PATH
    2. XDG specification paths
    3. System-specific paths
    4. Default Python paths
    5. Custom provider paths

    Returns:
        str: os.pathsep-separated path string
    """
    # Start with current PATH
    current_path = [Path(p) for p in os.environ.get("PATH", "").split(os.pathsep) if p]

    # Collect all potential paths
    all_paths: list[Path] = []
    all_paths.extend(current_path)
    all_paths.extend(get_xdg_paths())  # Now returns Path objects directly
    all_paths.extend(get_system_specific_paths())  # Now returns Path objects directly
    all_paths.extend(Path(p) for p in os.defpath.split(os.pathsep) if p)

    # Add paths from custom providers
    for provider in _path_providers:
        try:
            all_paths.extend(Path(p) for p in provider())
        except Exception:
            if os.environ.get("CLIFIND_DEBUG"):
                pass

    # Remove duplicates while preserving order
    seen = set()
    unique_paths = []
    for path in all_paths:
        if path and str(path) not in seen and path.is_dir():
            seen.add(str(path))
            unique_paths.append(path)

    return os.pathsep.join(str(p) for p in unique_paths)


def clear_path_cache() -> None:
    """Clear the cached PATH. Call this if environment variables change."""
    build_extended_path.cache_clear()


###############################
## DECORATORS & MAIN FUNCTION
###############################
"""
Application entry points and dependency management decorators:
- needs(): Auto-install decorator
- main(): CLI entry point
"""


def _install_with_uv(missing: list[str], target: bool) -> None:
    """
    Install missing packages using UV package manager.

    Args:
        missing: List of package names to install
        target: If True, install to UV_INSTALL_TARGET path, otherwise to Python environment

    Raises:
        RuntimeError: If UV installation fails
    """
    uv_cli = which_uv()
    if not uv_cli:
        msg = "UV package manager not found and could not be installed"
        raise RuntimeError(msg)

    cmd = [str(uv_cli), "pip", "install"]
    if target:
        cmd.extend(["--target", str(UV_INSTALL_TARGET)])
    else:
        cmd.extend(["--python", sys.executable])
    cmd.extend(missing)

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)

    if result.stdout:
        logging.debug(f"UV install output: {result.stdout}")


def _import_modules(modules: list[str]) -> None:
    """
    Import modules, raising clear errors if imports fail.

    Args:
        modules: List of module names to import

    Raises:
        RuntimeError: If any module fails to import
    """
    for mod in modules:
        try:
            importlib.import_module(mod)
        except ImportError as e:
            msg = f"Failed to import {mod} after installation: {e}"
            raise RuntimeError(msg)


def needs(mods: list[str], target: bool = False) -> Callable:
    """
    Decorator to auto-install missing dependencies using uv.

    Args:
        mods: List of module names to ensure are installed
        target: If True, install to UV_INSTALL_TARGET path, otherwise to Python environment

    Returns:
        Callable: Decorated function that ensures dependencies are installed

    Raises:
        RuntimeError: If UV is not available or installation fails
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            missing = [m for m in mods if not importlib.util.find_spec(m)]
            if missing:
                try:
                    _install_with_uv(missing, target)
                    _import_modules(missing)
                except subprocess.CalledProcessError as e:
                    msg = f"UV installation failed: {e.stderr}"
                    raise RuntimeError(msg)
                except Exception as e:
                    msg = f"Unexpected error during installation: {e!s}"
                    raise RuntimeError(msg)
            return f(*args, **kwargs)

        return wrapper

    return decorator


@needs(["fire", "pydantic"], target=False)
def main():
    import fire

    logging.info(repr(fire))
    return fire


if __name__ == "__main__":
    main()
