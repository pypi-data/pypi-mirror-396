# Installation

`tui-delta` can be installed via Homebrew, pipx, pip, or from source.

## Requirements

- **Python 3.9 or higher** (for pip/pipx installations)
- **Homebrew** (for macOS/Linux Homebrew installation - automatically installs syslog-ng)
- **syslog-ng 4.10.1+** (for pattern matching engine)

!!! warning "syslog-ng Dependency"
    `tui-delta` requires syslog-ng to be installed. See the [syslog-ng Installation Guide](../SYSLOG_NG_INSTALLATION.md) for platform-specific instructions.

    **Homebrew users:** syslog-ng is installed automatically as a dependency.

    **pip/pipx users:** You must install syslog-ng separately from official repositories before using tui-delta.

`tui-delta` works on Linux, macOS, and Windows (via WSL2).

## Via Homebrew (macOS/Linux) - Recommended

```bash
brew tap jeffreyurban/tui-delta
brew install tui-delta
```

**Automatically installs syslog-ng** as a dependency. Homebrew manages all dependencies and provides easy updates via `brew upgrade`.

## Via pipx (Cross-platform)

!!! warning "Install syslog-ng first"
    Before using pipx, you must install syslog-ng from official repositories.
    See [syslog-ng Installation Guide](../SYSLOG_NG_INSTALLATION.md) for detailed instructions.

```bash
# After installing syslog-ng (see link above):
pipx install tui-delta
```

[pipx](https://pipx.pypa.io/) installs in an isolated environment with global CLI access. Works on macOS, Linux, and Windows. Update with `pipx upgrade tui-delta`.

## Via pip

!!! warning "Install syslog-ng first"
    Before using pip, you must install syslog-ng from official repositories.
    See [syslog-ng Installation Guide](../SYSLOG_NG_INSTALLATION.md) for detailed instructions.

```bash
# After installing syslog-ng (see link above):
pip install tui-delta
```

Use `pip` if you want to use tui-delta as a library in your Python projects.

## Via Source

For development or the latest unreleased features:

```bash
git clone https://github.com/JeffreyUrban/tui-delta.git
cd tui-delta
pip install .
```

This installs `tui-delta` and its dependencies:

- **typer** - CLI framework
- **rich** - Terminal formatting and progress display
- **pyyaml** - YAML parsing

## Development Installation

For contributing or modifying `tui-delta`, install in editable mode with development dependencies:

```bash
git clone https://github.com/JeffreyUrban/tui-delta.git
cd tui-delta
pip install -e ".[dev]"
```

Development dependencies include:

- **pytest** - Test framework
- **pytest-cov** - Code coverage
- **ruff** - Linting and formatting
- **mypy** - Type checking
- **types-pyyaml** - Type stubs for YAML
- **pre-commit** - Git hooks for code quality

## Platform-Specific Notes

### Linux

Recommended installation methods:

- **Homebrew**: `brew tap jeffreyurban/tui-delta && brew install tui-delta`
- **pipx**: `pipx install tui-delta`
- **pip**: `pip install tui-delta`

!!! tip "Virtual Environments"
    If using pip directly, consider using a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install tui-delta
    ```

### macOS

Recommended installation methods:

- **Homebrew**: `brew tap jeffreyurban/tui-delta && brew install tui-delta` (recommended)
- **pipx**: `pipx install tui-delta`
- **pip**: `pip install tui-delta`

### Windows

Recommended installation methods:

- **pipx**: `pipx install tui-delta` (recommended)
- **pip**: `pip install tui-delta`

The `tui-delta` command will be available in your terminal after installation.

## Verify Installation

After installation, verify `tui-delta` is working:

```bash
tui-delta --version
tui-delta --help
```

## Upgrading

### Homebrew

```bash
brew upgrade tui-delta
```

### pipx

```bash
pipx upgrade tui-delta
```

### pip

```bash
pip install --upgrade tui-delta
```

### Source Installation

```bash
cd tui-delta
git pull
pip install --upgrade .
```

For development installations:

```bash
cd tui-delta
git pull
pip install --upgrade -e ".[dev]"
```

## Uninstalling

### Homebrew

```bash
brew uninstall tui-delta
```

### pipx

```bash
pipx uninstall tui-delta
```

### pip

```bash
pip uninstall tui-delta
```

## Troubleshooting

### Command Not Found

If `tui-delta` command is not found after installation:

1. **Check pip installed in the right location:**
   ```bash
   pip show tui-delta
   ```

2. **Verify Python scripts directory is in PATH:**
   ```bash
   python -m site --user-base
   ```
   Add `<user-base>/bin` to your PATH if needed.

3. **Use Python module syntax:**
   ```bash
   python -m tui-delta --help
   ```

### Import Errors

If you see import errors, ensure dependencies are installed:

```bash
pip install typer rich
```

Or reinstall with dependencies:

```bash
pip install --force-reinstall .
```

### Permission Errors

If you encounter permission errors, install for your user only:

```bash
pip install --user .
```

Or use a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install .
```

## Next Steps

- [Quick Start Guide](quick-start.md) - Learn basic usage
- [Basic Concepts](basic-concepts.md) - Understand how `tui-delta` works
- [CLI Reference](../reference/cli.md) - Complete command-line options
