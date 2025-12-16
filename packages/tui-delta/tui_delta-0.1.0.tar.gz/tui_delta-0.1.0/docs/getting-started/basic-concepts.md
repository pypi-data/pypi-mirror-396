# Basic Concepts

Understand the core concepts behind `tui-delta`.

## The Problem

AI assistant TUIs (like Claude Code) frequently redraw the screen with updated content. A typical session might:

1. Show a task with a spinner
2. Update the spinner character repeatedly
3. Replace the task line when complete
4. Show progress indicators that change frequently

Raw capture of this output contains thousands of duplicate/overwritten lines. `tui-delta` extracts only the meaningfully different content.

## How tui-delta Works

### 1. Capture with `script`

Uses the Unix `script` command to capture ALL terminal output, including:

- ANSI escape sequences (colors, cursor movement)
- Clear line sequences
- Control characters

### 2. Clear Line Detection

Identifies lines marked for clearing by the TUI application:

- Counts `ESC[2K` sequences (ANSI clear line)
- Applies profile-specific rules to determine what was cleared
- Marks lines as kept (+) or cleared (\\ and /)

### 3. Consolidate Cleared Blocks

Processes consecutive cleared blocks:

- First cleared block: output in full
- Subsequent blocks: output only changes vs previous block
- Normalizes patterns (e.g., spinner symbols, timestamps)

### 4. Deduplication

Removes duplicate sequences using `uniqseq`:

- Tracks sequences of lines
- Outputs only first occurrence
- Profile-specific tracking patterns

## Profiles

Profiles configure processing for different TUI applications:

- **claude_code** - Optimized for Claude Code sessions
  - Preserves submitted user input
  - Normalizes dialog questions and choices
  - Handles activity spinners and progress indicators

- **generic** - Basic processing for most TUIs
  - Only universal rules
  - Works with any TUI application

- **minimal** - Minimal processing
  - Only base clear detection
  - No protections or pattern normalization

## Output Format

Processed output:

- Preserves all colors and formatting
- Includes all ephemeral content (briefly shown then cleared)
- Removes redundant redraws
- Can be viewed with `less -R`
- Suitable for logging and archival

## Real-time Streaming

All processing happens in real-time:

- No buffering delays
- Output streams as session runs
- Suitable for monitoring and piping to other tools

## Next Steps

- **[Quick Start](quick-start.md)** - Try tui-delta with simple examples
- **[CLI Reference](../reference/cli.md)** - Complete command options
- **[Custom Profiles](../guides/custom-profiles.md)** - Create profiles for your TUI apps
