"""Command-line entry point for twat-ez."""

from __future__ import annotations

from twat_ez import __version__


def main() -> None:
    """Print package information for the lightweight twat-ez CLI."""
    print(f"twat-ez v{__version__}")


if __name__ == "__main__":
    main()
