"""twat-ez: Easy and convenient utilities for the twat ecosystem.

Provides :mod:`twat_ez.py_needs`, a module for managing runtime script
dependencies, locating executables on the system PATH, and downloading files
over HTTP.  Useful when writing standalone Python scripts that need to
self-install packages before running.

Key helpers in ``py_needs``:
- Discover and add FontLab / application-specific site-packages to ``sys.path``.
- Register custom path providers so tool-finding works across unusual setups.
- Download files with automatic HTTP redirect handling.
"""

from __future__ import annotations
from .__version__ import __version__


from twat_ez import py_needs

def main() -> None:
    """CLI entry point for twat-ez — prints version string."""
    print(f"twat-ez v{__version__}")


__all__ = ["__version__", "main", "py_needs"]
