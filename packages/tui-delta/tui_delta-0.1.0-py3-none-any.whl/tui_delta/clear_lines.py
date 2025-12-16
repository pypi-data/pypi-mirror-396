#!/usr/bin/env python3
"""
Clear-lines filter.

Detects lines with repeated [clear_line][cursor_up] patterns to identify
lines removed by screen redraws. N is the count of [clear_line] instances.

Clear operation rules are defined in clear_rules.yaml and can be configured
per TUI application using profiles.

Lines output maintain the same order as input.

Uses a FIFO buffer to support looking back and ahead.

FIFO terminology:
- Upstream = toward input (new lines, added to right/end)
- Downstream = toward output (old lines, removed from left/front)
"""

import re
import sys
from collections import deque
from collections.abc import Iterator
from pathlib import Path
from typing import Optional, cast

import typer

from .clear_rules import ClearRules

# Type alias for FIFO queue items
FifoItem = tuple[int, str]  # (line_number, content)

MAX_BUFFER_SIZE = 100

CONTROL_LINES = "[bracketed_paste_on]", "[sync_output_off]"


def extract_osc_window_title(line: str) -> Optional[str]:
    """
    Extract window title from OSC sequences in a line.

    OSC sequences: ESC ] Ps ; Pt BEL
    We look for: ESC]0;title or ESC]2;title (window title)

    Args:
        line: Line potentially containing OSC window title

    Returns:
        Extracted title or None
    """
    # Match OSC window title: ESC ] 0 ; title BEL (or ST)
    # BEL is \x07, ST is ESC \
    match = re.search(r"\x1b\](?:0|2);([^\x07\x1b]*?)(?:\x07|\x1b\\)", line)
    if match:
        return match.group(1)
    return None


def count_clear_sequences(line: str) -> int:
    """
    Count clear line ANSI sequences in a line.

    Clear line sequence: ESC [ K (erase from cursor to end of line)

    Args:
        line: Line to check

    Returns:
        Number of clear line sequences found
    """
    return line.count("\x1b[2K")


def clear_lines(
    fifo: deque[FifoItem],
    clear_count: int,
    show_prefixes: bool,
    show_line_numbers: bool,
    clear_operation_count: int,
    rules: ClearRules,
    next_line: Optional[str] = None,
) -> None:
    """
    Clear lines from the end of the FIFO

    Args:
        fifo: The FIFO deque of tuples (line_number, content)
        clear_count: The number of lines to clear
        show_prefixes: Whether to show state prefixes (+, \\, /, >)
        show_line_numbers: Whether to show line numbers
        clear_operation_count: Count of clear operations (for alternating prefix)
        rules: ClearRules instance with loaded configuration
        next_line: The line immediately after the clear line (for lookahead)
    """
    max_clearable = len(fifo) - 1  # Always keep at least the clear line itself

    # Get context for rule evaluation
    # Start with base clear count from rules
    lines_to_clear = clear_count - 1  # Base: N-1

    # Get first line that would be cleared (boundary)
    first_cleared_line = None
    if lines_to_clear > 0:
        first_cleared_index = len(fifo) - lines_to_clear - 1
        if 0 <= first_cleared_index < len(fifo):
            _, first_cleared_line = fifo[first_cleared_index]

    # Get first line of sequence (not cleared, the starting point)
    first_sequence_line = None
    if lines_to_clear > 0:
        first_sequence_index = len(fifo) - lines_to_clear - 1
        if 0 <= first_sequence_index < len(fifo):
            _, first_sequence_line = fifo[first_sequence_index]

    # Calculate actual clear count using rules
    actual_clear_count = rules.calculate_clear_count(
        clear_count, first_cleared_line, first_sequence_line, next_line
    )

    # Limit to available lines
    actual_clear_count = min(actual_clear_count, max_clearable)

    # Check if the clear line contains a window title annotation or OSC sequence
    # If so, we'll output it after the cleared block
    clear_line_content = fifo[-1][1] if fifo else ""
    window_title = None

    # Try extracting from raw OSC sequence first
    osc_title = extract_osc_window_title(clear_line_content)
    if osc_title:
        window_title = f"[window-title:{osc_title}]"
    # Fallback to legacy annotation format
    elif "[window-title-icon:" in clear_line_content or "[window-title:" in clear_line_content:
        # Extract the window title annotation
        # Note: content may contain [U+XXXX] tokens which have ] in them
        # Use non-greedy match to find the content until ][ or ]$
        match = re.search(r"\[(window-title(?:-icon)?:.+?)](?:\[|$)", clear_line_content)
        if match:
            window_title = f"[{match.group(1)}]"

    uncleared_count = (
        len(fifo) - actual_clear_count - 1
    )  # Lines to keep (excluding cleared lines and clear line)

    # Determine prefix for cleared lines (alternates between \ and /)
    clear_prefix = "\\: " if clear_operation_count % 2 == 0 else "/: "

    # Output all downstream lines that didn't get cleared (starting at index 0)
    for _ in range(uncleared_count):
        line_num, content = fifo.popleft()
        if content.startswith(CONTROL_LINES):
            prefix = ">: "
        else:
            prefix = "+: "
        try:
            output = _format_line(prefix, line_num, content, show_prefixes, show_line_numbers)
            print(output, flush=True)
        except BrokenPipeError:
            sys.stderr.close()
            # Still continue processing

    # Output all cleared lines in ascending order
    for _ in range(actual_clear_count):  # Lines marked as cleared
        line_num, content = fifo.popleft()
        try:
            output = _format_line(clear_prefix, line_num, content, show_prefixes, show_line_numbers)
            print(output, flush=True)
        except BrokenPipeError:
            sys.stderr.close()
            # Still continue processing

    # Output window title if present (as a control line after the cleared block)
    if window_title:
        try:
            # Use fake line number 0 for window title (it's metadata, not content)
            output = _format_line(">: ", 0, window_title, show_prefixes, show_line_numbers)
            print(output, flush=True)
        except BrokenPipeError:
            sys.stderr.close()
            return  # Exit on broken pipe

    fifo.popleft()  # Dispose of the clear line


def _format_line(
    prefix: str, line_num: int, content: str, show_prefixes: bool, show_line_numbers: bool
) -> str:
    """
    Format a line for output

    Args:
        prefix: State prefix (+: , \\: , /:, > )
        line_num: Line number
        content: Line content
        show_prefixes: Whether to show state prefix
        show_line_numbers: Whether to show line number

    Returns:
        Formatted line string
    """
    parts: list[str] = []
    if show_prefixes:
        parts.append(prefix)
    if show_line_numbers:
        parts.append(f"{line_num:010d}: ")
    parts.append(content)
    return "".join(parts)


app = typer.Typer()


@app.command()
def main(
    input_file: Optional[typer.FileText] = typer.Argument(None, help="Input file (default: stdin)"),
    show_prefixes: bool = typer.Option(
        False,
        "--prefixes/--no-prefixes",
        help=(
            "Show state prefixes "
            "(+: for kept, \\: and /: alternating for cleared, >: for control, )"
        ),
    ),
    show_line_numbers: bool = typer.Option(
        False, "--line-numbers/--no-line-numbers", "-n/-N", help="Show line numbers"
    ),
    buffer_size: int = typer.Option(
        MAX_BUFFER_SIZE,
        "--buffer-size",
        "-b",
        help="Maximum FIFO buffer size (limits memory usage for large files)",
    ),
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        "-p",
        help="Clear rules profile (claude_code, generic, minimal, or custom). Default: claude_code",
    ),
    rules_file: Optional[Path] = typer.Option(
        None, "--rules-file", help="Path to custom clear_rules.yaml file"
    ),
    list_profiles: bool = typer.Option(
        False, "--list-profiles", help="List available profiles and exit"
    ),
) -> None:
    """
    Filter to detect and mark cleared lines in terminal output.

    Reads from stdin (or file) and outputs selected lines based on options.
    By default, outputs only kept lines without prefixes or line numbers.

    Clear operation rules are defined in clear_rules.yaml and can be configured
    per TUI application using --profile.
    """
    # Handle --list-profiles
    if list_profiles:
        profiles = ClearRules.list_profiles(rules_file)
        print("Available profiles:")
        for name, description in profiles.items():
            print(f"  {name}: {description}")
        return

    # Load clear rules
    rules = ClearRules(config_path=rules_file, profile=profile)
    fifo: deque[FifoItem] = deque()
    line_number = 1
    clear_operation_count = 0

    # Handle binary vs text input
    # Read from binary stdin, decode UTF-8
    if input_file:
        input_stream = input_file.buffer
    else:
        input_stream = sys.stdin.buffer
    # Wrap to decode lines
    line_iterator = cast(
        Iterator[str],
        (line.decode("utf-8", errors="replace") for line in input_stream),  # type: ignore[union-attr]
    )

    try:
        # Read first line
        try:
            current_line = next(line_iterator)
        except StopIteration:
            return  # Empty input

        while True:
            content = current_line.rstrip("\n")

            # Try to read next line for lookahead
            try:
                next_line = next(line_iterator)
                next_line_content = next_line.rstrip("\n")
            except StopIteration:
                next_line_content = None
                next_line = None

            fifo.append((line_number, content))
            line_number += 1

            # Check if this is a clear-lines pattern
            # Support both raw ANSI (\x1b[K) and legacy annotations ([clear_line])
            clear_count = count_clear_sequences(content)
            if clear_count == 0:  # Fallback to legacy format
                clear_count = content.count("[clear_line]")

            if clear_count > 0:
                clear_lines(
                    fifo,
                    clear_count,
                    show_prefixes,
                    show_line_numbers,
                    clear_operation_count,
                    rules,
                    next_line_content,
                )
                clear_operation_count += 1

            while len(fifo) > buffer_size:
                line_num, content = fifo.popleft()
                if content.startswith(CONTROL_LINES):
                    prefix = ">: "
                else:
                    prefix = "+: "
                try:
                    output = _format_line(
                        prefix, line_num, content, show_prefixes, show_line_numbers
                    )
                    print(output, flush=True)
                except BrokenPipeError:
                    sys.stderr.close()
                    return

            # Move to next line
            if next_line is None:
                break  # We've processed the last line
            current_line = next_line

        # Output remaining lines
        while fifo:
            line_num, content = fifo.popleft()
            if content.startswith(CONTROL_LINES):
                prefix = ">: "
            else:
                prefix = "+: "
            try:
                output = _format_line(prefix, line_num, content, show_prefixes, show_line_numbers)
                print(output, flush=True)
            except BrokenPipeError:
                sys.stderr.close()
                return

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app()
