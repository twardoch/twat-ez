# this_file: src/twat_ez/__main__.py
"""Fire CLI entry point for twat-ez."""

from __future__ import annotations

import fire

from twat_ez import py_needs
from twat_ez.__version__ import __version__


def _version() -> str:
    """Print the installed twat-ez version."""
    return __version__


def _info() -> dict:
    """Show package info for twat-ez.

    Returns:
        Dict with package name, version, and description.
    """
    return {
        "package": "twat-ez",
        "version": __version__,
        "description": "Easy and convenient utilities for the twat ecosystem.",
        "modules": ["py_needs"],
        "note": "Use 'twat-ez py-needs' for runtime dependency management helpers.",
    }


def _py_needs_info(
    cmd: str | None = None,
    url: str | None = None,
    mode: int = 1,
) -> object:
    """Invoke py_needs utilities: find executables, download URLs, or show info.

    Args:
        cmd: Command name to locate on PATH (e.g. 'uv', 'pip').
        url: URL to download (returns content as string by default).
        mode: Download mode: 0=bytes, 1=str-or-bytes, 2=str (default: 1).

    Returns:
        Located path, downloaded content, or module info dict.
    """
    if cmd is not None:
        result = py_needs.which(cmd)
        return str(result) if result else f"'{cmd}' not found on PATH"
    if url is not None:
        return py_needs.download_url(url, mode=mode)
    # No args: show module info
    return {
        "module": "twat_ez.py_needs",
        "helpers": [
            "which(cmd) — locate an executable on the extended PATH",
            "which_uv() — locate the uv package manager",
            "which_pip() — locate pip",
            "download_url(url) — download a URL (Qt or urllib fallback)",
            "needs([mods]) — decorator: auto-install missing deps via uv",
            "get_site_packages_path() — return the active site-packages directory",
            "build_extended_path() — return the full extended PATH string",
        ],
    }


COMMANDS: dict[str, object] = {
    "version": _version,
    "info": _info,
    "py-needs": _py_needs_info,
}


def cmd_version() -> None:
    """Entry point: twat-ez-version."""
    fire.Fire(_version, name="twat-ez-version")


def cmd_info() -> None:
    """Entry point: twat-ez-info."""
    fire.Fire(_info, name="twat-ez-info")


def cmd_py_needs() -> None:
    """Entry point: twat-ez-py-needs."""
    fire.Fire(_py_needs_info, name="twat-ez-py-needs")


def main() -> None:
    """Fire CLI dispatcher for twat-ez."""
    fire.Fire(COMMANDS, name="twat-ez")


if __name__ == "__main__":
    main()
