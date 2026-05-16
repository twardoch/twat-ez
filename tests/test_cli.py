# this_file: tests/test_cli.py
"""CLI tests for twat-ez."""

from __future__ import annotations

import subprocess
import sys


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "twat_ez", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_help_exits_zero() -> None:
    """twat-ez --help exits 0 and prints output (Fire writes help to stderr)."""
    r = _run("--help")
    assert r.returncode == 0
    out = r.stdout + r.stderr
    assert out.strip()


def test_version_exits_zero() -> None:
    """twat-ez version prints a semver string."""
    r = _run("version")
    assert r.returncode == 0
    assert r.stdout.strip()


def test_version_looks_like_semver() -> None:
    """Version string contains at least one dot."""
    r = _run("version")
    assert "." in r.stdout


def test_info_exits_zero() -> None:
    """twat-ez info exits 0."""
    r = _run("info")
    assert r.returncode == 0
    assert "twat-ez" in r.stdout


def test_info_help() -> None:
    """twat-ez info --help exits 0."""
    r = _run("info", "--help")
    assert r.returncode == 0


def test_py_needs_help() -> None:
    """twat-ez py-needs --help exits 0."""
    r = _run("py-needs", "--help")
    assert r.returncode == 0


def test_py_needs_no_args() -> None:
    """twat-ez py-needs (no args) shows module info."""
    r = _run("py-needs")
    assert r.returncode == 0
    assert "py_needs" in r.stdout or "which" in r.stdout.lower()
