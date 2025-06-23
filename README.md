# twat-ez: Easy and Convenient Utilities for the `twat` Ecosystem

[![PyPI version](https://badge.fury.io/py/twat-ez.svg)](https://badge.fury.io/py/twat-ez)
[![Python Versions](https://img.shields.io/pypi/pyversions/twat-ez.svg)](https://pypi.org/project/twat-ez/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![GitHub Actions CI](https://github.com/twardoch/twat-ez/actions/workflows/push.yml/badge.svg)](https://github.com/twardoch/twat-ez/actions/workflows/push.yml)
[![GitHub Actions Release](https://github.com/twardoch/twat-ez/actions/workflows/release.yml/badge.svg)](https://github.com/twardoch/twat-ez/actions/workflows/release.yml)

`twat-ez` provides a set of easy-to-use and convenient utilities designed to enhance the `twat` ecosystem and simplify common Python scripting tasks. It primarily features the `py_needs` module, offering robust functionalities for path management, dynamic dependency installation, and URL content fetching.

## Rationale

The `twat` ecosystem often involves scripting and interaction with various command-line tools and external resources. `twat-ez` aims to:

*   **Simplify Script Dependencies:** Allow scripts to define and automatically install their Python package dependencies on-the-fly using `uv`, reducing setup friction.
*   **Robust Tool Discovery:** Provide a reliable way to find executables (`pip`, `uv`, custom tools) across different platforms and common user installation paths (including XDG directories).
*   **Convenient Downloads:** Offer a simple interface for downloading content from URLs, with built-in support for redirects and fallback mechanisms.
*   **Plugin Integration:** Serve as a plugin for the `twat` application, extending its capabilities.

The `py_needs.py` module is the cornerstone of this package, designed to be potentially usable as a standalone utility script or as an importable library component.

## Features

*   **`twat` Plugin:** Extends the `twat` application.
*   **`py_needs` Utility Module:**
    *   **Automated Dependency Installation:** Scripts can use the `@needs` decorator to specify and auto-install required Python packages via `uv`.
    *   **Smart Executable Discovery:** Enhanced `which` functionality to find CLIs in system, user, XDG, and custom paths.
    *   **Resilient URL Downloading:** Easy-to-use function to fetch content from URLs, handling redirects (with QtNetwork if available, falling back to `urllib`).
    *   **Configurable Installation Target:** Control where `@needs(target=True)` installs packages using the `UV_INSTALL_TARGET` environment variable.
*   **Modern Python:** PEP 621 compliant packaging with `pyproject.toml` and Hatch.
*   **Quality Assurance:**
    *   Type hints and static analysis with MyPy.
    *   Linting and formatting with Ruff.
    *   Comprehensive test suite using Pytest.
    *   Pre-commit hooks for maintaining code quality.
*   **CI/CD Ready:** GitHub Actions for automated testing, building, and publishing to PyPI.
*   **Dynamic Versioning:** Versioning based on Git tags via `hatch-vcs`.

## Installation

You can install `twat-ez` using `pip` or `uv`.

**Using `pip`:**

```bash
pip install twat-ez
```

**Using `uv`:**

```bash
uv pip install twat-ez
```

## Usage

### As a `twat` Plugin

Once installed, `twat-ez` can be utilized as a plugin within the `twat` ecosystem:

```python
import twat_ez

# The plugin might be automatically discovered by twat,
# or you might access its functionalities like this:
# (Refer to twat's documentation for specific plugin usage)
# plugin_interface = twat.get_plugin("ez")
# print(twat_ez.plugin) # Example placeholder
```
*(Note: The exact mechanism for plugin interaction depends on the `twat` application itself. The entry point `ez = "twat_ez"` is registered.)*

### Using the `py_needs.py` Module

The `py_needs` module offers several utilities for your Python scripts.

```python
from twat_ez import py_needs
```

#### 1. Finding Executables

Reliably find executables on the system path, including common user locations.

```python
# Find the 'git' executable
git_path = py_needs.which("git")
if git_path:
    print(f"Found git at: {git_path}")
else:
    print("git not found.")

# Find pip or uv
pip_path = py_needs.which_pip()
uv_path = py_needs.which_uv() # This will attempt to install uv via pip if not found

if pip_path:
    print(f"Found pip at: {pip_path}")
if uv_path:
    print(f"Found uv at: {uv_path}")
```

#### 2. Automated Dependency Installation with `@needs`

Ensure your script's dependencies are met automatically. The `@needs` decorator will check if specified packages are available and, if not, install them using `uv`.

```python
from twat_ez.py_needs import needs

@needs(["requests", "pydantic==2.x.x"]) # Specify packages, optionally with version constraints
def my_function_that_needs_requests_and_pydantic():
    import requests
    from pydantic import BaseModel

    # Your code here that uses requests and pydantic
    response = requests.get("https://jsonplaceholder.typicode.com/todos/1")
    print("Requests fetched:", response.json()["title"])

    class Item(BaseModel):
        id: int
        name: str

    item = Item(id=1, name="Test Item")
    print("Pydantic model created:", item.name)

my_function_that_needs_requests_and_pydantic()
```

**Targeted Installation with `@needs(target=True)`:**

By default, `@needs` installs packages into the current Python environment. If you want to install packages to a custom location (e.g., a user-specific directory for tools rather than a project virtual environment), you can use `target=True`.

```python
@needs(["some-cli-tool"], target=True)
def run_tool():
    # some-cli-tool will be installed to the location specified by
    # UV_INSTALL_TARGET, or a default user site-packages directory.
    subprocess.run(["some-cli-tool", "--version"], check=True)

# To control the installation path for target=True:
# Set the UV_INSTALL_TARGET environment variable before running the script.
# Example (Linux/macOS):
# export UV_INSTALL_TARGET="/path/to/my/tools/python_libs"
# python your_script.py
#
# Example (Windows PowerShell):
# $env:UV_INSTALL_TARGET = "C:\path\to\my\tools\python_libs"
# python your_script.py
```
If `UV_INSTALL_TARGET` is not set, it defaults to a standard user site-packages directory (e.g., `~/.local/lib/pythonX.Y/site-packages` on Linux).

#### 3. Downloading Content from URLs

Fetch content from URLs, with support for redirects. It prioritizes `PythonQt.QtNetwork` if available (often in environments like FontLab), falling back to Python's built-in `urllib`.

```python
# Download as bytes (mode=0)
try:
    binary_content = py_needs.download_url("https://example.com/somefile.zip", mode=0)
    with open("downloaded_file.zip", "wb") as f:
        f.write(binary_content)
    print("File downloaded successfully.")
except RuntimeError as e:
    print(f"Download error: {e}")

# Download as string (mode=2, forces UTF-8 decoding)
try:
    text_content = py_needs.download_url("https://jsonplaceholder.typicode.com/todos/1", mode=2)
    print("Text content:", text_content[:100] + "...") # Print first 100 chars
except RuntimeError as e:
    print(f"Download error: {e}")
except UnicodeDecodeError:
    print("Failed to decode content as UTF-8.")

# Download as string, fallback to bytes on decode error (mode=1, default)
try:
    flexible_content = py_needs.download_url("https://example.com")
    if isinstance(flexible_content, str):
        print("Content (string):", flexible_content[:100] + "...")
    else:
        print(f"Content (bytes, could not decode as UTF-8): {len(flexible_content)} bytes")
except RuntimeError as e:
    print(f"Download error: {e}")
```

## Technical Codebase Structure (`py_needs.py`)

The core logic of this package resides primarily in `src/twat_ez/py_needs.py`. This module is structured internally as follows:

*   **Path Providers & Environment Functions:**
    *   Manages system path discovery, including XDG paths and OS-specific binary locations.
    *   Includes logic for finding FontLab-specific Python paths.
    *   Provides `build_extended_path()` for a comprehensive executable search path.
*   **Utility Functions:**
    *   `verify_executable()`: Basic security checks for executables.
    *   `bin_or_str()`: Data conversion utility.
*   **URL Download Functions:**
    *   Implements `download_url_qt()` using `PythonQt.QtNetwork` (if available).
    *   Provides `download_url_py()` using `urllib` as a fallback.
    *   `download_url()` is the main interface that attempts Qt then falls back to `urllib`.
*   **UV Installation Helpers:**
    *   `which_uv()`: Locates the `uv` executable, attempting to install it via `pip` if not found.
    *   `which_pip()`: Locates the `pip` executable, attempting to bootstrap with `ensurepip` if needed.
    *   `which()`: The enhanced executable locator.
*   **Decorators & Main Function:**
    *   `@needs()`: The decorator for auto-installing dependencies.
    *   `_install_with_uv()`, `_import_modules()`: Helper functions for the `@needs` decorator.
    *   A `main()` function for potential direct script execution (e.g., if `py_needs.py` is run as a script, though its primary use is as a module).

The `py_needs.py` file also includes a shebang and a `/// script ... ///` block allowing it to be run directly with `uv run ./src/twat_ez/py_needs.py ...` if its own script dependencies (like `fire`) are managed this way.

## Development

This project uses [Hatch](https://hatch.pypa.io/) for development workflow management. Hatch environments are configured to use `uv` for faster dependency installation.

### Setup Development Environment

1.  **Install Hatch and pre-commit:**
    ```bash
    # Using pip
    pip install hatch pre-commit
    # Or using uv
    uv pip install hatch pre-commit
    ```

2.  **Activate Hatch Environment:**
    This creates a virtual environment (or reuses an existing one) and installs dependencies, including the project itself in editable mode.
    ```bash
    hatch shell
    ```
    You are now in the project's development environment.

3.  **Install Pre-commit Hooks:**
    (Run this once after cloning the repository)
    ```bash
    pre-commit install
    ```
    This will ensure that linters and formatters run on your changed files before you commit.

### Common Development Tasks

(Ensure you are in the Hatch shell: `hatch shell`)

*   **Run Tests:**
    ```bash
    hatch run test
    ```
    Or, to pass arguments to pytest:
    ```bash
    hatch run test -- tests/test_twat_ez.py -k "some_test_name"
    ```

*   **Run Tests with Coverage:**
    ```bash
    hatch run test-cov
    ```
    This will output a coverage report to the terminal and generate an XML report.

*   **Linting and Formatting:**
    Ruff is used for both.
    *   Check for linting issues and formatting:
        ```bash
        hatch run lint:style
        ```
    *   Auto-format code and fix linting issues (where possible):
        ```bash
        hatch run lint:fmt
        ```
        Pre-commit hooks will also run these checks.

*   **Type Checking:**
    MyPy is used for static type checking.
    ```bash
    hatch run type-check
    ```
    Or, for more detailed output and to install missing stubs:
    ```bash
    hatch run lint:typing
    ```

### Versioning and Releases

*   **Versioning:** Versioning is managed automatically by `hatch-vcs` based on Git tags. The version is derived from the latest tag and commit history.
*   **Releases:** Releases to PyPI are automated via GitHub Actions when a new tag matching the pattern `v*.*.*` (e.g., `v0.1.0`) is pushed to the repository. The workflow will build the package and publish it.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
