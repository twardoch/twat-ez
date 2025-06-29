# twat-ez: Easy and Convenient Utilities for the `twat` Ecosystem

[![PyPI version](https://badge.fury.io/py/twat-ez.svg)](https://badge.fury.io/py/twat-ez)
[![Python Versions](https://img.shields.io/pypi/pyversions/twat-ez.svg)](https://pypi.org/project/twat-ez/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![GitHub Actions CI](https://github.com/twardoch/twat-ez/actions/workflows/push.yml/badge.svg)](https://github.com/twardoch/twat-ez/actions/workflows/push.yml)
[![GitHub Actions Release](https://github.com/twardoch/twat-ez/actions/workflows/release.yml/badge.svg)](https://github.com/twardoch/twat-ez/actions/workflows/release.yml)

`twat-ez` is a Python library that provides a collection of easy-to-use utilities designed to enhance the `twat` ecosystem and simplify common Python scripting tasks. Its core component, the `py_needs` module, offers powerful features for managing script dependencies, finding tools and executables, and downloading files from the web.

## Part 1: Getting Started with `twat-ez`

This section is for anyone looking to understand what `twat-ez` does, who can benefit from it, and how to quickly get it up and running.

### What is `twat-ez`?

At its heart, `twat-ez` aims to make Python scripting more robust and less cumbersome. Whether you're writing standalone scripts or extending the `twat` application, `twat-ez` provides tools to handle common challenges:

*   **Effortless Dependency Management:** Automatically install required Python packages for your scripts on-the-fly.
*   **Reliable Tool Discovery:** Find system executables (like `git`, `pip`, or custom tools) without worrying about diverse user environments.
*   **Convenient Web Downloads:** Fetch content from URLs with built-in support for redirects and flexible decoding.
*   **`twat` Ecosystem Enhancement:** Serves as a plugin for the `twat` application, extending its capabilities.

### Who is it for?

`twat-ez` is designed for:

*   **Python Developers & Scripters:** Anyone writing Python scripts that need to interact with system tools, manage their own dependencies, or fetch data from the web.
*   **Users of the `twat` Ecosystem:** Individuals leveraging the `twat` application can benefit from the extended functionalities `twat-ez` provides as a plugin.
*   **Developers in Specialized Environments:** Useful for those working with Python in environments that might have their own package management or specific path configurations (e.g., within applications like FontLab which bundle Python).

### Why is it useful?

`twat-ez` offers several benefits to streamline your development workflow:

*   **Reduced Setup Friction:** Scripts can define and install their own dependencies using the `@needs` decorator. This means users don't have to manually `pip install` packages before running your script.
*   **Increased Script Portability:** The enhanced tool discovery mechanism (`py_needs.which`) reliably finds executables across different operating systems and common installation locations (including standard system paths, user binary directories, and XDG paths).
*   **Simplified Web Interaction:** The `download_url` function handles complexities like HTTP redirects and offers options for how content is returned (bytes or string), trying to use efficient QtNetwork libraries if available.
*   **Extensibility for `twat`:** As a plugin, it seamlessly integrates with and expands the `twat` application's feature set.
*   **Modern and Maintained:** Built with modern Python practices, type-hinted, linted, tested, and actively maintained.

### Key Features Overview

*   **`@needs` Decorator:** Just decorate a function with `@needs(["package_a", "package_b"])`, and `twat-ez` will ensure these packages are installed (using `uv`) before your function runs.
*   **Smart Executable Locator (`py_needs.which`):** An improved `which` command that searches an extensive set of paths, making your scripts more resilient to different environment setups.
*   **Resilient URL Downloader (`py_needs.download_url`):** A simple function to get content from the web, with automatic redirect following and fallback mechanisms.
*   **`twat` Plugin Integration:** Designed to work as part of the `twat` application.

### Installation

You can install `twat-ez` using `pip` or `uv`:

**Using `pip`:**

```bash
pip install twat-ez
```

**Using `uv`:**

```bash
uv pip install twat-ez
```

### Usage Guide

`twat-ez` can be used as a plugin for the `twat` application or as a standalone Python library, primarily through its `py_needs` module.

#### As a `twat` Plugin

Once installed, `twat-ez` is available as a plugin within the `twat` ecosystem. The `pyproject.toml` registers an entry point `ez = "twat_ez"`. The specific way to interact with it as a plugin will depend on the `twat` application's plugin management system.

*(Refer to the `twat` application's documentation for details on how it discovers and uses plugins.)*

#### Programmatic Usage with `py_needs`

The `py_needs` module is the workhorse of `twat-ez`. Import it into your scripts:

```python
from twat_ez import py_needs
```

Here are some common use cases:

##### 1. Finding Executables

Reliably locate executables on the system, searching standard paths, user-specific paths (like `~/.local/bin`), and XDG directories.

```python
# Find the 'git' executable
git_path = py_needs.which("git")
if git_path:
    print(f"Found git at: {git_path}")
else:
    print("git not found.")

# Find pip (will try to bootstrap with ensurepip if not found and not discoverable)
pip_path = py_needs.which_pip()
if pip_path:
    print(f"Found pip at: {pip_path}")
else:
    print("pip not found or bootstrap failed.")

# Find uv (will attempt to install uv via pip if not found)
uv_path = py_needs.which_uv()
if uv_path:
    print(f"Found uv at: {uv_path}")
else:
    print("uv not found and could not be installed.")
```

##### 2. Automated Dependency Installation with `@needs`

Ensure your script's Python package dependencies are met automatically. The `@needs` decorator checks for specified packages and, if missing, installs them using `uv`.

```python
from twat_ez.py_needs import needs

@needs(["requests", "pydantic==2.*"]) # Specify packages, optionally with version constraints
def fetch_todo_and_validate():
    import requests
    from pydantic import BaseModel

    class Todo(BaseModel):
        userId: int
        id: int
        title: str
        completed: bool

    response = requests.get("https://jsonplaceholder.typicode.com/todos/1")
    response.raise_for_status() # Ensure the request was successful
    todo_data = response.json()

    todo = Todo(**todo_data)
    print(f"Fetched Todo: {todo.title} (Completed: {todo.completed})")

fetch_todo_and_validate()
```

**Targeted Installation with `@needs(target=True)`:**

By default, `@needs` installs packages into the current Python environment's site-packages. If you want to install packages to a custom location (e.g., a user-specific directory for tools, separate from project virtual environments), use `target=True`.

The installation path for `target=True` is determined by the `UV_INSTALL_TARGET` environment variable. If not set, it defaults to a standard user site-packages directory (e.g., `~/.local/lib/pythonX.Y/site-packages` on Linux, or a FontLab-specific path if detected).

```python
from twat_ez.py_needs import needs
import subprocess

@needs(["cowsay"], target=True) # For demo; 'cowsay' is usually a system package
def cowsay_a_message():
    # 'cowsay' (if it were a Python CLI tool) would be installed to UV_INSTALL_TARGET.
    try:
        # Ensure the bin dir of UV_INSTALL_TARGET is in your PATH
        subprocess.run(["cowsay", "Hello from twat-ez!"], check=True)
    except FileNotFoundError:
        print("cowsay command not found. Is UV_INSTALL_TARGET/bin in your PATH?")
    except subprocess.CalledProcessError as e:
        print(f"cowsay execution failed: {e}")

# To control the installation path for target=True:
# export UV_INSTALL_TARGET="/path/to/my/tools/python_libs" # (Linux/macOS)
# $env:UV_INSTALL_TARGET = "C:\\path\\to\\my\\tools\\python_libs" # (Windows PowerShell)
# python your_script.py

# cowsay_a_message() # Uncomment to run
```
**Important:** For executables installed with `target=True` to be runnable directly, the `bin` directory of your `UV_INSTALL_TARGET` (e.g., `/path/to/my/tools/python_libs/bin`) must be in your system's `PATH` environment variable.

##### 3. Downloading Content from URLs

Fetch content from URLs, with automatic redirect handling. It prioritizes `PythonQt.QtNetwork` if available (often in environments like FontLab), falling back to Python's built-in `urllib`.

```python
# Download as bytes (mode=0)
try:
    binary_content = py_needs.download_url("https://via.placeholder.com/150", mode=0)
    with open("placeholder_image.png", "wb") as f:
        f.write(binary_content)
    print("Image downloaded successfully as placeholder_image.png.")
except RuntimeError as e:
    print(f"Download error: {e}")

# Download as string (mode=2, forces UTF-8 decoding)
try:
    text_content = py_needs.download_url("https://jsonplaceholder.typicode.com/todos/1", mode=2)
    print(f"Text content (first 100 chars): {text_content[:100]}...")
except RuntimeError as e:
    print(f"Download error: {e}")
except UnicodeDecodeError:
    print("Failed to decode content as UTF-8.")

# Download as string, fallback to bytes on decode error (mode=1, default)
try:
    flexible_content = py_needs.download_url("https://example.com")
    if isinstance(flexible_content, str):
        print(f"Content from example.com (string, first 100 chars): {flexible_content[:100]}...")
    else:
        print(f"Content from example.com (bytes, could not decode as UTF-8): {len(flexible_content)} bytes")
except RuntimeError as e:
    print(f"Download error: {e}")
```

#### Command-Line Usage (`py_needs.py`)

The `py_needs.py` module itself can be invoked as a script using `uv run` (due to its embedded script metadata) or `python -m twat_ez.py_needs`. This exposes its functions (like `download_url`, `which`, etc.) as CLI commands, powered by the `fire` library.

**Example:**

To use the `download_url` function from the command line:

```bash
# Using uv run (if you have the source code)
uv run ./src/twat_ez/py_needs.py download_url --url="https://example.com" --mode=2

# Using python -m (after installing twat-ez)
python -m twat_ez.py_needs download_url --url="https://example.com" --mode=2
```

This will print the content of `example.com` to standard output. You can explore other functions similarly. Use `--help` to see the available commands and their options:

```bash
uv run ./src/twat_ez/py_needs.py -- --help
python -m twat_ez.py_needs -- --help
```
*(Note: The double dash `--` is used with `uv run` to separate arguments for `uv run` itself from arguments for the script. For `python -m`, it's used to signal end of options for `python` and start of options for the script if the script itself parses options in a way that might conflict.)*

---

## Part 2: Technical Deep Dive & Contribution Guide

This section provides a more detailed look into the internal workings of `twat-ez`, particularly the `py_needs.py` module, and outlines the project's structure and contribution guidelines.

### `py_needs.py`: Core Functionality Internals

The primary logic of `twat-ez` resides in `src/twat_ez/py_needs.py`. This module is designed to be highly functional, potentially even usable as a standalone script in some contexts, thanks to its `uv run` compatibility.

#### Overall Architecture

`py_needs.py` is structured into several key areas:
*   **Path Providers & Environment Functions:** Manages system path discovery and environment interactions.
*   **Utility Functions:** Core helpers for tasks like executable verification.
*   **URL Download Functions:** Implements network content retrieval.
*   **UV Installation Helpers:** Manages the `uv` package manager lifecycle and related `pip` discovery.
*   **Decorators & Main Function:** Includes the `@needs` decorator and the CLI entry point.

#### Path Management and Executable Discovery

A robust mechanism for finding executables is crucial for scripts that need to call external tools.

*   **`build_extended_path()`:** This is the cornerstone of executable discovery. It constructs a comprehensive `PATH` string by concatenating paths from several sources in a specific order:
    1.  The current `PATH` environment variable.
    2.  XDG specification paths (see `get_xdg_paths()`).
    3.  System-specific common binary locations (see `get_system_specific_paths()`).
    4.  Default Python paths (`os.defpath`).
    5.  Paths from any custom path providers registered via `register_path_provider()`.
    The resulting list is deduplicated while preserving order, and only includes existing directories. This function's output is LRU cached via `functools.lru_cache`.

*   **`get_xdg_paths()`:** Retrieves paths based on the XDG Base Directory Specification. It checks `XDG_BIN_HOME` and the parent `bin` directory of `XDG_DATA_HOME` (e.g., `$XDG_DATA_HOME/../bin`). If these are not set, it defaults to `~/.local/bin` if it exists.

*   **`get_system_specific_paths()`:** Provides a list of common executable locations tailored to the operating system:
    *   **macOS:** Includes `/usr/local/bin`, `/opt/homebrew/bin` (for Apple Silicon Homebrew), standard system bins, and Xcode paths.
    *   **Windows:** Includes user AppData paths, System32, PowerShell paths, and Chocolatey paths.
    *   **Linux/Other:** Includes standard system bins and `/snap/bin` if it exists.

*   **`which(cmd, mode=os.F_OK | os.X_OK, path=None, verify=True)`:** This is an enhanced version of `shutil.which`. It uses the path string generated by `build_extended_path()` (or a custom one if provided) to search for the command `cmd`.
    *   If `verify=True` (default), after finding an executable, it calls `verify_executable()` on it. If verification fails, `which` returns `None`.
    *   The result is LRU cached.

*   **`verify_executable(path_to_exe)`:** Performs basic security and sanity checks on a potential executable:
    *   Ensures the path exists and is a regular file.
    *   On Unix-like systems, checks if the file is world-writable (mode `0o002`), returning `False` (unsafe) if it is.
    *   (Currently, Windows checks are minimal beyond existence and file type).

*   **`which_pip()`:** Locates the `pip` executable.
    1.  It first calls `py_needs.which("pip")`.
    2.  If not found, it attempts to bootstrap `pip` using `ensurepip.bootstrap()`.
    3.  After attempting bootstrap, it tries `py_needs.which("pip")` again.
    4.  It also tries to locate `pip` via `importlib.util.find_spec("pip")` as a final fallback.
    *   The result is LRU cached.

*   **`which_uv()`:** Locates the `uv` executable.
    1.  It first calls `py_needs.which("uv")`.
    2.  If `uv` is not found, it attempts to install `uv` for the current user by calling `pip install --user uv` (using the `pip` found by `which_pip()`).
    3.  After an installation attempt, it calls `py_needs.which("uv")` again.
    *   The result is LRU cached.

*   **FontLab Integration (`_get_fontlab_site_packages()` and `get_site_packages_path()`):**
    *   `_get_fontlab_site_packages()`: Checks if running within FontLab (via `import fontlab`) and if so, constructs the path to FontLab's specific `site-packages` directory if it's in `sys.path`.
    *   `get_site_packages_path()`: Uses `_get_fontlab_site_packages()` first. If FontLab is not detected or its site-packages aren't relevant, it falls back to `site.getusersitepackages()`. This path is used as the default for `UV_INSTALL_TARGET`.

#### Dependency Management (`@needs` decorator)

The `@needs` decorator enables functions to declare their Python package dependencies, which are then auto-installed if missing.

*   **Workflow:**
    1.  When a function decorated with `@needs(mods_list, target=False)` is called, it iterates through `mods_list`.
    2.  For each module name, `importlib.util.find_spec(mod_name)` checks if the module is installed and importable.
    3.  Missing modules are collected. If any, `_install_with_uv(missing_list, target_flag)` is invoked.
    4.  After a successful installation, `_import_modules(missing_list)` attempts to import them, raising an error if they're still unavailable.

*   **`_install_with_uv(missing_packages, target_flag)`:**
    *   Locates `uv` using `which_uv()`.
    *   Constructs the command: `uv pip install <packages...>`.
    *   If `target_flag` is `True`:
        *   Appends `--target <path>` to the `uv` command. The `<path>` is from the `UV_INSTALL_TARGET` environment variable, defaulting to the output of `get_site_packages_path()`.
    *   If `target_flag` is `False`:
        *   Appends `--python <sys.executable>` to install into the current Python environment.
    *   Uses `subprocess.run()` for installation. Failures raise a `RuntimeError`.

*   **`UV_INSTALL_TARGET` Environment Variable:** Controls the installation directory for `@needs(target=True)`. This is useful for creating isolated tool-specific environments.

#### URL Downloading (`download_url`)

Provides a resilient method to fetch content from HTTP/HTTPS URLs.

*   **Priority System & Fallback:**
    1.  Attempts `download_url_qt()` if `PythonQt.QtNetwork` is importable (common in FontLab).
    2.  If `PythonQt` is unavailable or `download_url_qt()` fails, it falls back to `download_url_py()`.
    *   Successful downloads are LRU cached.

*   **`download_url_qt(url, mode, max_redir)`:**
    *   Uses `PythonQt.QtNetwork.QNetworkAccessManager` and `PythonQt.QtCore.QEventLoop` for synchronous handling of Qt's asynchronous network operations.
    *   Manually handles HTTP redirects (301, 302, 303, 307, 308) up to `max_redir` times.

*   **`download_url_py(url, mode, max_redir)`:**
    *   Uses Python's `urllib.request.build_opener()` and `urlopen()`.
    *   `urllib` handles redirects automatically. `max_redir` mainly ensures interface consistency.

*   **`bin_or_str(data_bytes, mode)`:** Converts downloaded `bytes` based on `mode`:
    *   `mode=0`: Raw `bytes`.
    *   `mode=1` (default): UTF-8 `str`; falls back to `bytes` on `UnicodeDecodeError`.
    *   `mode=2`: UTF-8 `str`; raises `UnicodeDecodeError` on failure.

#### Caching (`functools.lru_cache`)

Several functions in `py_needs.py` use `@lru_cache` for performance by memoizing results:
*   `download_url_qt`, `download_url_py`, `download_url`
*   `which_uv`, `which_pip`, `which`
*   `build_extended_path`
Caches can be cleared programmatically (e.g., `py_needs.which.cache_clear()`).

#### Standalone Script Capability & CLI (`main`)

`py_needs.py` has a shebang (`#!/usr/bin/env -S uv run`) and an embedded `/// script ... ///` block (specifying `fire` as a dependency). This enables execution via `uv run ./src/twat_ez/py_needs.py <command> [args...]`.
The `if __name__ == "__main__":` block calls `main()`, which is set up to use `fire`. `fire.Fire()` (implicitly called) exposes the public functions of `py_needs.py` (e.g., `download_url`, `which`) as CLI commands.

### Project Structure and Packaging

*   **`src/twat_ez/__init__.py`:** Contains the package version (`__version__`), dynamically sourced from `importlib.metadata.version`.
*   **`pyproject.toml`:** Central configuration for build and packaging:
    *   **Build System:** `hatchling` backend with `hatch-vcs` for Git tag-based dynamic versioning. The version is written to `src/twat_ez/__version__.py` by `hatch-vcs` during build.
    *   **Metadata:** Defines name (`twat-ez`), Python version (`>=3.10`), license (MIT).
    *   **Dependencies:** Runtime (`twat>=1.8.1`) and optional (`dev`, `test`).
    *   **Entry Points:** Registers `twat-ez` as a `twat` plugin: `[project.entry-points."twat.plugins"]` with `ez = "twat_ez"`.
    *   **Hatch (`tool.hatch`):** Configures `uv` as the installer for Hatch environments. Defines environments (`default`, `lint`) and scripts for tasks like testing (`test`, `test-cov`), type checking (`type-check`), and linting (`lint`).
*   **Tests (`tests/test_twat_ez.py`):** Pytest-based unit and integration tests.

### Coding Standards and Contribution Guide

This project follows modern Python practices for quality and maintainability.

#### 1. Development Environment

*   **Hatch:** Used for environment management. [Install Hatch](https://hatch.pypa.io/latest/install/), then run `hatch shell`. This uses `uv` to create/update a virtual environment with all dependencies.
*   **Pre-commit Hooks:** Configured in `.pre-commit-config.yaml` for automated linting/formatting. Install with `pre-commit install`.

#### 2. Code Quality

*   **Ruff:** For linting and formatting. Configured in `pyproject.toml` (`[tool.ruff]`).
    *   Check: `hatch run lint:style`
    *   Format & Fix: `hatch run lint:fmt`
*   **MyPy:** For static type checking. Configured in `pyproject.toml` (`[tool.mypy]`).
    *   Check: `hatch run type-check` (or `hatch run lint:typing`).
*   **Type Hinting:** All new code should be fully type-hinted.

#### 3. Testing

*   **Pytest:** Tests are in the `tests` directory.
    *   Run: `hatch run test`
    *   Coverage: `hatch run test-cov`. Configured in `pyproject.toml` (`[tool.coverage]`).
*   New features and bug fixes require corresponding tests.

#### 4. Versioning and Releases

*   **Versioning:** `hatch-vcs` derives versions from Git tags (Semantic Versioning, e.g., `v0.1.0`).
*   **Releases:** Pushing a `v*.*.*` tag to `main` on GitHub triggers the `release.yml` GitHub Action to build and publish to PyPI.

#### 5. Commit Messages

*   Strive for clear, descriptive messages. Consider [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat: ...`, `fix: ...`).

#### 6. Branching and Pull Requests

*   Develop on feature branches (from `main`).
*   Submit changes via Pull Requests to `main`. PRs are reviewed and must pass CI checks (GitHub Actions `push.yml`).

#### 7. Issue Tracking

*   Use [GitHub Issues](https://github.com/twardoch/twat-ez/issues) for bugs, features, and discussions.

#### 8. License

*   MIT License. Contributions are accepted under this license. See [LICENSE](LICENSE) file.
