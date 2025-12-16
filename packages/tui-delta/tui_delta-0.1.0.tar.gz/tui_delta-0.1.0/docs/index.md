# tui-delta

**Run a TUI application (AI assistant sessions, et al) with real-time delta processing for monitoring and logging. Supports Claude Code.**

A general-purpose TUI capture and logging utility created for efficiently logging AI assistant interactive sessions.

## Why tui-delta?

**Simpler utilities lose content.** Because TUI applications update the display by erasing content, simpler TUI logging utilities that fast forward through the session capture only the final screen state and miss most of the session's interactions, work, and status indications.

**tui-delta preserves all meaningful deltas.** Intelligently processes terminal output to maintain all meaningful content while removing only redundant redraws.

Captures and logs TUI applications efficiently, streaming all meaningfully different content in real-time.

## Primary Use Case

Log AI assistant sessions (Claude Code, Cline, Cursor, Aider, etc.) with:

- **Complete capture** - All meaningful content preserved
- **Real-time streaming** - Monitor sessions as they run
- **Clean output** - Removes only redundant redraws, not meaningful content
- **Preserves appearance** - Logs viewable with `less -R` show original formatting

## Quick Example

<!-- interactive-only -->
```console
$ tui-delta --profile claude_code -- claude code > session.log
```

This wraps Claude Code, processes its output in real-time, and saves to `session.log` while displaying to terminal.

## How It Works

1. **Wraps TUI application** using `script` to capture all terminal output
2. **Detects cleared lines** - Identifies content that was overwritten
3. **Consolidates changes** - Outputs only meaningful differences
4. **Deduplicates sequences** - Removes redundant output using profile-specific patterns
5. **Streams to stdout** - All output available immediately for piping or logging

## Features

- **Profile-based Processing** - Pre-configured for Claude Code, plus support for user-specified profiles
- **Custom Profiles** - Define YAML profiles for other TUI applications
- **Real-time Streaming** - No unnecessary delays, output streams as session runs
- **Unix Pipeline Friendly** - Works with standard command-line tools and logging software

## Getting Started

- [Installation](getting-started/installation.md) - Install tui-delta
- [Quick Start](getting-started/quick-start.md) - Log your first AI assistant session
- [Basic Concepts](getting-started/basic-concepts.md) - Understand how tui-delta works

## Documentation Sections

- **[Getting Started](getting-started/installation.md)** - Installation and quick start
- **[Use Cases](use-cases/ai-assistants/ai-assistants.md)** - Real-world applications
- **[Guides](guides/custom-profiles.md)** - Custom profiles and configuration
- **[Reference](reference/cli.md)** - CLI and Python API documentation
- **[About](about/contributing.md)** - Contributing and development
