# twat-ez

**Easy and convenient utilities for the `twat` ecosystem.**

`twat-ez` is a `twat` plugin that provides runtime dependency management, enhanced executable discovery, and URL downloading for Python scripts and the `twat` application.

## Role in the twat ecosystem

`twat-ez` registers as the `ez` plugin (`twat.plugins` entry point), so the `twat` host can dispatch to it via `twat ez`. Its primary value is the `py_needs` module, which handles the "plumbing" that standalone Python scripts often need:

- Self-installing missing packages before a function runs
- Reliably finding executables across diverse OS environments (macOS Homebrew, Linux XDG, Windows AppData, FontLab bundles)
- Fetching URL content with automatic redirect following

## Installation

```bash
pip install twat-ez
# or
uv pip install twat-ez
```

## Quick start

```python
from twat_ez import py_needs

# Auto-install missing deps before the function runs
@py_needs.needs(["requests", "rich"])
def fetch_and_display(url: str) -> None:
    import requests, rich
    rich.print(requests.get(url).text)

# Find executables across extended PATH
uv_path = py_needs.which_uv()       # Path | None
pip_path = py_needs.which_pip()     # Path | None
git_path = py_needs.which("git")    # Path | None

# Download a URL (Qt if available, else urllib)
content = py_needs.download_url("https://example.com/data.txt")
```

## CLI usage

```bash
twat-ez                  # print version
twat-ez version          # print version
twat-ez info             # package metadata
twat-ez py-needs         # list py_needs helpers
twat-ez py-needs --cmd git      # locate 'git' on PATH
twat-ez py-needs --url https://example.com  # download URL
```

Or equivalently:

```bash
python -m twat_ez version
```

## py_needs API

### `@needs(mods, *, target=False)`

Decorator that ensures all listed modules are importable before the decorated function runs. Missing modules are installed via `uv pip install`.

```python
@py_needs.needs(["httpx", "pydantic"])
def my_script() -> None:
    import httpx, pydantic
    ...
```

`target=True` installs into `UV_INSTALL_TARGET` (defaults to the active site-packages directory) instead of the current Python environment.

### `which(cmd, *, verify=True) -> Path | None`

Enhanced `shutil.which` that searches current `PATH`, XDG paths, system-specific directories (Homebrew, snap, Windows AppData), and any registered custom providers.

```python
path = py_needs.which("ffmpeg")
```

### `which_uv() -> Path | None`

Locate `uv`. Falls back to installing via `pip --user uv` if not found.

### `which_pip() -> Path | None`

Locate `pip`. Falls back to `ensurepip.bootstrap()` if not found.

### `download_url(url, mode=1, max_redir=5) -> bytes | str`

Download a URL. Tries Qt (`PythonQt.QtNetwork`) first, falls back to `urllib`. Results are LRU-cached.

- `mode=0` — return `bytes`
- `mode=1` — return `str` if UTF-8 decodable, else `bytes` (default)
- `mode=2` — return `str`, raise `UnicodeDecodeError` if not decodable

### `register_path_provider(fn)`

Register a callable `() -> list[str]` that contributes additional directories to the PATH used by `which`. Useful for FontLab or other embedded Python environments.

```python
def my_app_bin() -> list[str]:
    return ["/MyApp.app/Contents/Resources/bin"]

py_needs.register_path_provider(my_app_bin)
```

### `get_site_packages_path() -> Path`

Returns the FontLab site-packages path if running inside FontLab, otherwise the user site-packages directory.

### `build_extended_path() -> str`

Returns the full `os.pathsep`-separated PATH string used by `which`. Cached; call `clear_path_cache()` after environment changes.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `UV_INSTALL_TARGET` | user site-packages | Install target for `needs(..., target=True)` |
| `CLIFIND_DEBUG` | unset | Enable debug output in `which` / path building |
