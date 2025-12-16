# TUI Delta

**Run a TUI application (AI assistant sessions, et al) with real-time delta processing for monitoring and logging. Supports Claude Code.**

A general-purpose TUI capture and logging utility created for efficiently logging AI assistant interactive sessions.

**Why tui-delta?** Simpler utilities that strip screen control sequences result in substantial content loss. `tui-delta` intelligently processes terminal output to preserve all meaningful deltas while removing only redundancies, creating clean, complete logs suitable for real-time monitoring and archival.

Fully supports Claude Code; other AI assistants (Cline, Cursor, Aider) are expected to work with profile customization.

[![PyPI version](https://img.shields.io/pypi/v/tui-delta.svg)](https://pypi.org/project/tui-delta/)
[![Tests](https://github.com/JeffreyUrban/tui-delta/actions/workflows/test.yml/badge.svg)](https://github.com/JeffreyUrban/tui-delta/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/JeffreyUrban/tui-delta/branch/main/graph/badge.svg)](https://codecov.io/gh/JeffreyUrban/tui-delta)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/readthedocs/tui-delta)](https://tui-delta.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

**Requirements:** Python 3.9+, syslog-ng 4.10.1+

> **⚠️ Important:** `tui-delta` requires syslog-ng to be installed from **official repositories** (distro defaults may be incompatible).
>
> See **[SYSLOG_NG_INSTALLATION.md](docs/SYSLOG_NG_INSTALLATION.md)** for platform-specific instructions.

### Via Homebrew (macOS + Linux) - Recommended

```bash
brew tap JeffreyUrban/tui-delta && brew install tui-delta
```

**✅ Automatically installs syslog-ng** as a dependency. Homebrew manages all dependencies and provides easy updates via `brew upgrade`.

### Via pipx (Alternative)

> **⚠️ Manual Setup Required:** You must install syslog-ng separately before using pipx.

```bash
# STEP 1: Install syslog-ng from official repos (REQUIRED)
# See docs/SYSLOG_NG_INSTALLATION.md for your platform

# STEP 2: Install tui-delta
pipx install tui-delta
```

[pipx](https://pipx.pypa.io/) installs in an isolated environment with global CLI access. Update with `pipx upgrade tui-delta`.

### Via pip

> **⚠️ Manual Setup Required:** You must install syslog-ng separately before using pip.

```bash
# STEP 1: Install syslog-ng from official repos (REQUIRED)
# See docs/SYSLOG_NG_INSTALLATION.md for your platform

# STEP 2: Install tui-delta
pip install tui-delta
```

Use `pip` if you want to use tui-delta as a library in your Python projects.

### From Source

```bash
# Development installation
git clone https://github.com/JeffreyUrban/tui-delta
cd tui-delta
pip install -e ".[dev]"
```

### Windows

Windows is not currently supported. Consider using WSL2 (Windows Subsystem for Linux) and following the Linux installation instructions.

**Requirements:** Python 3.9+, syslog-ng (installed automatically with Homebrew)

## Quick Start

### Logging a Claude Code Session

```bash
# Run Claude Code with tui-delta processing
tui-delta --profile claude_code -- claude code

# Output streams to stdout in real-time
# You can pipe to logging tools, redirect to file, etc.
```

### View Captured Logs

Logs preserve the original terminal appearance and are viewable with standard tools:

```bash
# View with less (supports colors and formatting)
less -R session.log

# Follow in real-time
tui-delta --profile claude_code -- claude code > session.log

# Monitor with tail
tui-delta --profile claude_code -- claude code > session.log &
tail -f session.log
```

## Use Cases

- **AI Assistant Logging** - Capture Claude Code sessions (fully supported); others expected to work with custom profiles
- **Real-time Monitoring** - Stream processed output to monitoring tools while the session runs
- **TUI Development** - Debug terminal applications by seeing all content changes
- **Education** - Record and share AI-assisted coding sessions with clean, readable logs

## How It Works

Unlike simpler approaches that strip control sequences (losing content), `tui-delta` intelligently processes terminal output to preserve all meaningful deltas:

1. **Capture** - Uses `script` to capture all terminal output including control sequences
2. **Clear Detection** - Identifies lines that were cleared/overwritten
3. **Consolidation** - Outputs all meaningful changes, removing only redundant redraws
4. **Deduplication** - Removes duplicate sequences using configurable patterns
5. **Streaming** - All output streams in real-time to stdout for immediate use

**Result:** Complete, accurate logs of what happened in the session - not just the final terminal state.

`tui-delta` leverages [`patterndb-yaml`](https://github.com/JeffreyUrban/patterndb-yaml) for multi-line pattern recognition via `syslog-ng`, and [`uniqseq`](https://github.com/JeffreyUrban/uniqseq) for deduplication of repeated content blocks.

## Documentation

**[Read the full documentation at tui-delta.readthedocs.io](https://tui-delta.readthedocs.io/)**

Key sections:
- **Getting Started** - Installation and quick start guide
- **Use Cases** - Real-world examples across different domains
- **Guides** - Profile selection and definition, common patterns
- **Reference** - Complete CLI and Python API documentation

## Development

```bash
# Clone repository
git clone https://github.com/JeffreyUrban/tui-delta.git
cd tui-delta-workspace/tui-delta

# Install development dependencies
pip install -e ".[dev]"

# Complete initial project setup
# Prompt Claude Code: "Please perform Initial Project Kickoff"

# Run tests
pytest

# Run with coverage
pytest --cov=tui-delta --cov-report=html
```

## Features

- **Profile-based Processing** - Pre-configured profiles for Claude Code, generic TUI apps, and minimal processing
- **Custom Profiles** - Define your own YAML profiles for different TUI applications
- **Real-time Streaming** - Output streams as the session runs, no buffering delays
- **Preserves Appearance** - Logs show content exactly as displayed in terminal
- **Efficient Deduplication** - Smart removal of redundant content while keeping ephemeral changes
- **Unix Pipeline Friendly** - Works with standard Unix tools

## License

MIT License - See [LICENSE](LICENSE) file for details

## Author

Jeffrey Urban

---

**[Star on GitHub](https://github.com/JeffreyUrban/tui-delta)** | **[Report Issues](https://github.com/JeffreyUrban/tui-delta/issues)**
