# Logging AI Assistant Sessions

Primary use case: capturing and logging AI assistant interactive sessions.

## AI Assistant Compatibility

- **Claude Code** - Fully supported with optimized profile
- **Cline, Cursor, Aider, etc.** - Expected to work; likely requires profile customization for best results

**Note:** Only Claude Code is supported. Other assistants are expected to work, with custom profiles necessary for optimal results. Community contributions welcome.

## Claude Code Sessions

### Basic Logging

<!-- interactive-only -->
```console
$ tui-delta run --profile claude_code -- claude code > session.log
```

Captures the full session with everything visible in the view and scrollback:

- User prompts and assistant responses
- Tool use (file reads, writes, commands)
- Ephemeral content (status reports, active files, etc.)
- Dialog interactions
- Window titles

### Real-time Monitoring + Logging

<!-- interactive-only -->
```console
$ tui-delta run --profile claude_code -- claude code > session.log
```

Interact in terminal AND save to file simultaneously.

### Review Logged Session

<!-- interactive-only -->
```console
$ less -R session.log
```

The `-R` flag may be necessary to preserve ANSI colors and formatting on some systems.

### Plain Text Logs

For clean plain text logs without ANSI colors or formatting:

**Using sed (most portable):**
```bash
tui-delta run --profile claude_code -- claude code | \
  sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' > clean-session.log
```

**Using ansifilter (recommended if available):**
```bash
# Install
brew install ansifilter  # macOS
apt install ansifilter   # Ubuntu/Debian

# Use
tui-delta run --profile claude_code -- claude code | \
  ansifilter > clean-session.log
```

This is useful for:
- Processing logs with tools that don't handle ANSI codes
- Reducing log file size
- Clean text for documentation or sharing
- Simpler grep/analysis without color codes

## Other AI Assistants

Start with the `generic` profile:

<!-- interactive-only -->
```console
$ tui-delta run --profile generic -- aider
$ tui-delta run --profile generic -- cursor
$ tui-delta run --profile generic -- cline
```

For best results, you'll likely need to create a custom profile. See [Custom Profiles](../../guides/custom-profiles.md).

**Community contributions:** We welcome profile contributions for other AI assistants!

## Use Cases

### Session Archival

Keep records of AI-assisted development sessions:

<!-- interactive-only -->
```console
$ tui-delta run --profile claude_code -- claude code \
  > "session-$(date +%Y%m%d-%H%M%S).log"
```

Creates timestamped log files for each session.

### Review and Learning

Review past sessions to:

- Understand what changes were made
- Learn from assistant's suggestions
- Document project decisions
- Share examples with team

### Debugging

When unexpected behavior occurs:

<!-- interactive-only -->
```console
$ tui-delta run --profile claude_code -- claude code 2>&1 > full-session.log
```

Captures both stdout and stderr for debugging.

## Log Format

Logged sessions:

- Preserve original terminal appearance
- Include all meaningful content changes
- Remove redundant screen redraws
- Viewable with standard Unix tools (`less`, `grep`, etc.)

!!! tip "Monitoring output while logging"
    To monitor output while logging, redirect to a file and monitor with `tail -f` in another terminal:

    ```bash
    tui-delta run -- claude code > session.log
    # Then in another terminal:
    tail -f session.log
    ```

    Note: `tui-delta run -- claude code | tee session.log` will likely garble the display since tee's stdout competes with the TUI.

## Integration with Logging Tools

### Append to Daily Log

<!-- interactive-only -->
```console
$ tui-delta run --profile claude_code -- claude code \
  >> daily-$(date +%Y%m%d).log
```

### Pipe to Analysis Tools

!!! note "Output to terminal may garble display"
    When piping to utilities like `grep`, `tail`, etc., their output to the terminal will likely compete with the TUI display, resulting in garbled output. Redirecting to a file or processing logs after the session completes avoids this issue.

**Redirect output to avoid garbling:**
```bash
# Save to file during session
tui-delta run --profile claude_code -- claude code | \
  grep -i "error" > errors.log

# Or process log after session completes
tui-delta run --profile claude_code -- claude code > session.log
grep -i "error" session.log
```

**Output to terminal (likely garbles display):**
```bash
# grep output competes with TUI display
tui-delta run --profile claude_code -- claude code | grep -i "error"
```

### Stream to Remote Logging

```bash
# logger sends to syslog, not terminal
tui-delta run --profile claude_code -- claude code | logger -t claude-code
```

## Next Steps

- **[Quick Start](../../getting-started/quick-start.md)** - Get started quickly
- **[Custom Profiles](../../guides/custom-profiles.md)** - Create profiles for other assistants
