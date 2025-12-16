# CLI Reference

Complete command-line reference for `tui-delta`.

## Commands

### `tui-delta run`

Run a TUI application with real-time delta processing.

**Usage:**

```console
$ tui-delta run [OPTIONS] -- COMMAND...
```

**Arguments:**

- `COMMAND...` - The TUI command to run (e.g., `claude code`, `npm test`)

**Options:**

- `--profile`, `-p` TEXT - Clear rules profile (claude_code, generic, minimal, or custom)
- `--rules-file` FILE - Path to custom clear_rules.yaml file
- `--help`, `-h` - Show help message

**Examples:**

Basic usage with Claude Code:

```console
$ tui-delta run --profile claude_code -- claude code > session.log
```

Use generic profile for other TUI apps:

```console
$ tui-delta run --profile generic -- aider
```

Custom rules file:

```console
$ tui-delta run --rules-file my-rules.yaml -- ./myapp
```

**Pipeline:**

The `run` command processes output through:

```
script → clear_lines → consolidate → uniqseq → cut → additional_pipeline
```

Where `additional_pipeline` is profile-specific (e.g., final uniqseq for claude_code).

### `tui-delta list-profiles`

List available clear rules profiles.

**Usage:**

```console
$ tui-delta list-profiles
```

**Example output:**

```console
$ tui-delta list-profiles
Available profiles:
  claude_code: Claude Code terminal UI (claude.ai/code)
  generic: Generic TUI with only universal rules
  minimal: Minimal - only base rule, no protections
```

## Profiles

### claude_code

Optimized for Claude Code terminal UI sessions.

**Features:**

- Preserves submitted user input (final occurrence)
- Normalizes dialog questions and choices
- Handles activity spinners
- Tracks thinking indicators
- Maintains scrollback output
- Deduplicates task progress updates
  - (keeping the last instance shown... e.g. generally the total token count for an action)

**Use when:** Logging Claude Code sessions

### generic

Basic processing for most TUI applications.

**Features:**

- Universal clear detection
- Blank line boundary protection
- No pattern normalization

**Use when:** Logging any TUI application, or as starting point for custom profiles

### minimal

Minimal processing with only base clear detection.

**Features:**

- Base clear count formula (N-1)
- No protections
- No pattern normalization

**Use when:** Debugging or maximum raw output

## Output

All commands output to stdout. Use shell redirection to save:

```console
$ tui-delta run -- claude code > session.log  # Display and save
$ tui-delta run -- claude code 2>&1 > full-log.txt  # Include stderr
```

## Exit Codes

- `0` - Success
- `1` - Error in pipeline stage
- TUI application's exit code is preserved

## Environment

### Terminal Size

The `script` command used by tui-delta respects terminal size. Set `COLUMNS` and `LINES` for consistent output:

```console
$ COLUMNS=120 LINES=40 tui-delta run -- claude code
```

## Next Steps

- **[Quick Start](../getting-started/quick-start.md)** - Get started quickly
- **[Custom Profiles](../guides/custom-profiles.md)** - Create your own profiles
