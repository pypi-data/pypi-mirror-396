#!/usr/bin/env python3
"""
Consolidate cleared blocks filter.

Processes output from clear_lines.py (with --prefixes --output both) to consolidate
consecutive cleared blocks by showing only the changes between them.

Kept blocks (+: prefix) are passed through unchanged.
For consecutive cleared blocks (\\: and /: prefixes):
- First cleared block in sequence: output in full
- Subsequent cleared blocks: output only changes vs previous cleared block

Multi-line sequence buffering:
- Sequences defined in tui_profiles.yaml under 'patterns'
- Each sequence has a leader pattern and follower patterns
- Sequences are extracted from blocks and buffered
- Buffered sequences output only before first block without the sequence
- Supports any sequences defined with 'sequence' field

Configuration:
- Loads normalization patterns from tui_profiles.yaml
- All patterns are available; profiles determine which rules are used upstream
"""

import difflib
import re
import sys
import tempfile
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

import typer
import yaml
from patterndb_yaml import PatterndbYaml  # type: ignore[import-untyped]
from rich.console import Console
from rich.text import Text

# Compile ANSI escape sequence regex once at module import time
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def _create_rules_file_from_profiles() -> Path:
    """
    Create a temporary normalization rules file from tui_profiles.yaml.

    Converts all pattern definitions from dict format to the rules list
    format expected by PatterndbYaml.

    Returns:
        Path to temporary YAML file in rules format
    """
    module_dir = Path(__file__).parent
    profiles_path = module_dir / "tui_profiles.yaml"

    with open(profiles_path) as f:
        config = yaml.safe_load(f)

    # Get all pattern definitions
    all_patterns = config.get("patterns", {})

    # Convert all patterns from dict to rules list format
    rules: list[dict[str, Any]] = []
    for pattern_name, pattern_def in all_patterns.items():
        # Add 'name' field for rules list format
        rule = {"name": pattern_name, **pattern_def}
        rules.append(rule)

    # Create temp file with rules in expected format
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
    yaml.safe_dump({"rules": rules}, temp_file)
    temp_file.close()

    return Path(temp_file.name)


class LineType(str, Enum):
    """Type of line based on prefix"""

    KEPT = "kept"
    CLEARED_BACKSLASH = "cleared_backslash"
    CLEARED_SLASH = "cleared_slash"
    COMMAND = "command"


def parse_line(line: str) -> tuple[LineType, str]:
    """
    Parse a line to extract its type and content.

    Args:
        line: Input line (may have prefix)

    Returns:
        Tuple of (line_type, content_without_prefix)
    """
    if line.startswith("+: "):
        return LineType.KEPT, line[3:]
    elif line.startswith(">: "):
        return LineType.COMMAND, line[3:]
    elif line.startswith("\\: "):
        return LineType.CLEARED_BACKSLASH, line[3:]
    elif line.startswith("/: "):
        return LineType.CLEARED_SLASH, line[3:]
    else:
        # TODO: Once complete and vetted, change to report the error and continue.
        raise ValueError(f"Unrecognized line prefix: {line[:3]}")


def is_window_title_line(content: str) -> bool:
    """
    Check if a line is a window title annotation.

    Args:
        content: Line content (without prefix)

    Returns:
        True if this is a window title line
    """
    return content.startswith("[window-title:") or content.startswith("[window-title-icon:")


def _char_diff(old_line: str, new_line: str) -> Text:
    """
    Compute character-level diff for two lines. Outputs two lines.

    Args:
        old_line: Original line content
        new_line: New line content
    Returns:
        diff_text with character-level highlighting
    """
    matcher = difflib.SequenceMatcher(None, old_line, new_line)

    diff_text = Text()

    # Convert opcodes to list so we can look ahead
    opcodes = list(matcher.get_opcodes())
    i = 0
    while i < len(opcodes):
        tag, _i1, _i2, j1, j2 = opcodes[i]

        if tag == "equal":
            diff_text.append(new_line[j1:j2])
            i += 1
        elif tag == "delete":
            # Check if next operation is insert - if so, treat as replacement (yellow)
            if i + 1 < len(opcodes) and opcodes[i + 1][0] == "insert":
                # Skip the delete, process the insert as yellow
                _, _, _, j1_next, j2_next = opcodes[i + 1]
                diff_text.append(new_line[j1_next:j2_next], style="yellow")
                i += 2  # Skip both delete and insert
            else:
                # Pure delete - show a single red marker character
                diff_text.append("␡", style="red")
                i += 1
        elif tag == "insert":
            # Check if previous operation was delete - if so, already handled
            if i > 0 and opcodes[i - 1][0] == "delete":
                # Already handled as part of delete+insert pair
                i += 1
            else:
                # Pure insert - show in green
                diff_text.append(new_line[j1:j2], style="green")
                i += 1
        elif tag == "replace":
            # Replacement - show new in yellow
            diff_text.append(new_line[j1:j2], style="yellow")
            i += 1

    return diff_text


def _match_pattern_components(
    line: str, pattern_components: list[dict[str, Any]]
) -> tuple[bool, dict[str, Any]]:
    """
    Generic pattern matcher.

    Args:
        line: Line to match against (ANSI codes will be stripped)

    Returns:
        Tuple of (matched: bool, fields: dict)
    """
    # Strip ANSI codes from line (use precompiled ANSI_RE)
    line_clean = ANSI_RE.sub("", line)

    pos = 0  # Current position in line_clean
    fields: dict[str, Any] = {}  # Extracted field values

    for component in pattern_components:
        if pos > len(line_clean):
            return False, {}  # Ran past end of line

        if "alternatives" in component:
            # Try to match any alternative at current position
            matched = False
            for alt in component["alternatives"]:
                # Each alternative is a list of elements
                alt_text = _render_component_sequence(alt)
                if line_clean[pos:].startswith(alt_text):
                    pos += len(alt_text)
                    matched = True
                    break

            if not matched:
                return False, {}  # No alternative matched

        elif "field" in component:
            # Extract field value from current position
            parser = component.get("parser")

            if parser == "NUMBER":
                # Match digits
                match = re.match(r"\d+", line_clean[pos:])
                if not match:
                    return False, {}
                pos += len(match.group())
            else:
                pos = len(line_clean)

        elif "text" in component:
            # Fixed text must match exactly
            text = component["text"]
            if not line_clean[pos:].startswith(text):
                return False, {}
            pos += len(text)

        elif "serialized" in component:
            # Serialized characters must match exactly
            serialized_str = component["serialized"]
            if not line_clean[pos:].startswith(serialized_str):
                return False, {}
            pos += len(serialized_str)

    return True, fields


def _render_component_sequence(components: list[dict[str, Any]]) -> str:
    """
    Render a sequence of pattern components to their literal text.

    Args:
        components: List of component dicts (text, serialized, etc.)

    Returns:
        Concatenated text representation
    """
    result: list[str] = []
    for comp in components:
        if "text" in comp:
            result.append(comp["text"])
        elif "serialized" in comp:
            result.append(comp["serialized"])
        # Fields and alternatives not supported in literal rendering
    return "".join(result)


def _print_prefixed_line(
    prefix: str,
    line: Union[Text, str],
    console: Optional[Console],
    style: Optional[str] = None,
) -> None:
    """
    Print a line with the given prefix, using Rich when a console is provided.

    Args:
        prefix: The prefix to show (e.g., "\\: " or "/: ")
        line: The line content; may be a plain string or a Rich Text object
        console: Optional Rich console; if provided, use it for styled output
        style: Optional style to apply to the line text when using Rich
    """
    if console:
        if isinstance(line, Text):
            console.print(Text(prefix, style="bold") + line)
        else:
            text = Text()
            text.append(prefix, style="bold")
            if style:
                text.append(line, style=style)
            else:
                text.append(line)
            console.print(text)
    else:
        # Plain stdout
        print(f"{prefix}{line}")


def _extract_sequence_block(
    lines: list[str],
    normalized_lines: list[str],
    sequence_configs: Optional[dict[str, Any]],
    sequence_markers: Optional[set[str]],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """
    Extract multi-line sequences from a block, separating them from non-sequence lines.

    Uses greedy extraction: when a leader line is found, immediately start extracting
    followers until we hit a line that doesn't match. No lookahead required.

    Optimized to use pre-normalized lines and markers for fast leader detection.

    Args:
        lines: Block lines to process (raw content)
        normalized_lines: Pre-normalized versions of lines (from PatterndbYaml)
        sequence_configs: Dict mapping rule names to rule configs
            (all rules with 'sequence' field)
        sequence_markers: Set of output prefixes that identify sequence leaders
            (e.g., "[dialog-question:")

    Returns:
        Tuple of (non_sequence_lines, sequence_lines, non_sequence_normalized, sequence_normalized)
    """
    if not sequence_configs or not sequence_markers:
        return lines, [], normalized_lines, []

    non_sequence: list[str] = []
    sequence_block: list[str] = []
    non_sequence_norm: list[str] = []
    sequence_norm: list[str] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        norm_line = normalized_lines[i]

        # Fast check: does normalized line start with any sequence marker?
        matched_sequence = None
        for marker in sequence_markers:
            if norm_line.startswith(marker):
                # Find which sequence config this marker belongs to
                for _rule_name, sequence_config in sequence_configs.items():
                    output = sequence_config.get("output", "")
                    if output.startswith("[") and ":" in output:
                        config_marker = output[: output.index(":") + 1]
                        if config_marker == marker:
                            matched_sequence = sequence_config
                            break
                break

        if matched_sequence:
            # Start extracting: add leader
            sequence_block.append(line)
            sequence_norm.append(norm_line)
            i += 1

            # Get follower patterns for this sequence
            sequence_spec = matched_sequence.get("sequence", {})
            follower_specs = sequence_spec.get("followers", [])

            # Greedily consume follower lines using generic pattern matching
            while i < len(lines):
                # Check if line matches any follower pattern
                matches_follower = any(
                    _match_pattern_components(lines[i], follower["pattern"])[0]
                    for follower in follower_specs
                )
                if matches_follower:
                    sequence_block.append(lines[i])
                    sequence_norm.append(normalized_lines[i])
                    i += 1
                else:
                    # Not a follower - stop extracting sequence
                    break
            continue

        # Not part of a sequence
        non_sequence.append(line)
        non_sequence_norm.append(norm_line)
        i += 1

    return non_sequence, sequence_block, non_sequence_norm, sequence_norm


def normalize(norm_engine: Optional[PatterndbYaml], lines: list[str]) -> list[str]:  # type: ignore[valid-type]
    """Normalize lines using optimized batch API (no StringIO overhead)."""
    if norm_engine is None:
        return lines
    return norm_engine.normalize_lines(lines)  # type: ignore[no-any-return]


def output_diff(
    prev_lines: list[str],
    curr_lines: list[str],
    prefix: str,
    console: Optional[Console] = None,
    use_diff: bool = False,
    norm_engine: Optional[PatterndbYaml] = None,  # type: ignore[valid-type]
    buffered_choices: Optional[list[tuple[str, str]]] = None,
    sequence_configs: Optional[dict[str, Any]] = None,
    sequence_markers: Optional[set[str]] = None,
) -> list[str]:
    """
    Output differences between two cleared blocks using proper diff algorithm.

    Args:
        prev_lines: Previous cleared block content (without prefixes)
        curr_lines: Current cleared block content (without prefixes)
        prefix: Prefix to use for output (\\: or /: )
        console: Optional Rich console for diff output
        use_diff: Whether to use diff output
        norm_engine: PatterndbYaml for normalizing lines before comparison
        buffered_choices: Optional list to accumulate sequence lines (will be modified)
        sequence_configs: Optional dict of all sequence configurations to extract and buffer
        sequence_markers: Optional set of sequence leader markers for fast detection

    Returns:
        List of sequence lines from current block (to update buffer)
    """
    # Normalize lines once for both diff comparison and sequence extraction
    prev_normalized = normalize(norm_engine, prev_lines)
    curr_normalized = normalize(norm_engine, curr_lines)

    # Fast check: do any lines contain sequence markers?
    has_sequences = False
    if sequence_markers:
        for norm_line in prev_normalized + curr_normalized:
            if any(norm_line.startswith(marker) for marker in sequence_markers):
                has_sequences = True
                break

    # Only extract sequences if we found sequence markers
    if has_sequences:
        prev_non_seq, _prev_seq, prev_non_seq_norm, _prev_seq_norm = _extract_sequence_block(
            prev_lines, prev_normalized, sequence_configs, sequence_markers
        )
        curr_non_seq, curr_seq, curr_non_seq_norm, _curr_seq_norm = _extract_sequence_block(
            curr_lines, curr_normalized, sequence_configs, sequence_markers
        )
    else:
        # No sequences - use all lines as non-sequence
        prev_non_seq, _prev_seq, prev_non_seq_norm, _prev_seq_norm = (
            prev_lines,
            [],
            prev_normalized,
            [],
        )
        curr_non_seq, curr_seq, curr_non_seq_norm, _curr_seq_norm = (
            curr_lines,
            [],
            curr_normalized,
            [],
        )

    # If current block has no sequence but we have buffered sequence, output it first
    if not curr_seq and buffered_choices:
        for seq_prefix, seq_line in buffered_choices:
            print(f"{seq_prefix}{seq_line}")

    # Use the non-sequence portions for diff (already normalized)
    prev_lines = prev_non_seq
    curr_lines = curr_non_seq

    prev_normalized = prev_non_seq_norm
    curr_normalized = curr_non_seq_norm

    # Use difflib to compute proper diff with insertions/deletions
    matcher = difflib.SequenceMatcher(None, prev_normalized, curr_normalized)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            # Lines are the same, skip them
            continue
        elif tag == "delete":
            # Lines removed from previous block
            pass
        elif tag == "insert":
            # Lines added in current block
            for line in curr_lines[j1:j2]:
                _print_prefixed_line(
                    prefix,
                    line,
                    console if use_diff else None,
                    style=("green" if use_diff else None),
                )
        elif tag == "replace":
            # Lines changed
            # Apply character-level diff if diff enabled
            if use_diff and console and len(prev_lines[i1:i2]) == 1 and len(curr_lines[j1:j2]) == 1:
                old_line = prev_lines[i1]
                new_line = curr_lines[j1]
                diff_text = _char_diff(old_line, new_line)

                # Show new version with character highlights
                _print_prefixed_line(prefix, diff_text, console)
            else:
                # No markers - just show the new version
                for line in curr_lines[j1:j2]:
                    _print_prefixed_line(prefix, line, console if use_diff else None)

    # Return the sequence lines from current block (for buffer update)
    return curr_seq


def _output_first_cleared_block(
    current_cleared_block: list[str],
    current_prefix: str,
    norm_engine: Optional[PatterndbYaml],  # type: ignore[valid-type]
    sequence_configs: Optional[dict[str, Any]],
    sequence_markers: Optional[set[str]],
    buffered_choices: list[tuple[str, str]],
) -> None:
    """
    Output the first cleared block in a sequence in full, while extracting and buffering
    any multi-line sequence lines so they can be emitted before the first subsequent block
    that does not contain the sequence.

    This mirrors the existing logic used at three call sites.
    """
    # Extract and buffer sequences from first block
    curr_normalized = normalize(norm_engine, current_cleared_block)

    non_sequence, sequence, _, _ = _extract_sequence_block(
        current_cleared_block, curr_normalized, sequence_configs, sequence_markers
    )

    # Output non-sequence content
    for cleared_line in non_sequence:
        print(f"{current_prefix}{cleared_line}")

    # Buffer sequence if any
    if sequence:
        buffered_choices[:] = [(current_prefix, line) for line in sequence]


def _flush_pending_cleared_block(
    previous_cleared_block: list[str],
    current_cleared_block: list[str],
    current_prefix: str,
    console: Optional[Console],
    use_diff: bool,
    norm_engine: Optional[PatterndbYaml],  # type: ignore[valid-type]
    buffered_choices: list[tuple[str, str]],
    sequence_configs: Optional[dict[str, Any]],
    sequence_markers: Optional[set[str]],
) -> None:
    """
    Flush a pending cleared block according to whether this is the first block in a
    sequence or a subsequent one that should be diffed against the previous.

    Side-effects:
    - Prints lines to stdout
    - Updates buffered_choices in-place
    """
    if previous_cleared_block:
        # Output diff vs previous
        curr_choices = output_diff(
            previous_cleared_block,
            current_cleared_block,
            current_prefix,
            console,
            use_diff,
            norm_engine,
            buffered_choices,
            sequence_configs,
            sequence_markers,
        )
        # Update or clear buffered choices based on current block
        if curr_choices:
            buffered_choices[:] = [(current_prefix, line) for line in curr_choices]
        else:
            buffered_choices.clear()
    else:
        _output_first_cleared_block(
            current_cleared_block,
            current_prefix,
            norm_engine,
            sequence_configs,
            sequence_markers,
            buffered_choices,
        )


app = typer.Typer()


@app.command()
def main(
    input_file: Optional[typer.FileText] = typer.Argument(None, help="Input file (default: stdin)"),
    diff: bool = typer.Option(
        False,
        "--diff/--no-diff",
        help=(
            "Use Git-style diffs with character-level highlighting "
            "(green=added, red=deleted, yellow=modified)"
        ),
    ),
):
    """
    Consolidate consecutive cleared blocks by showing only changes.

    Reads output from clear_lines.py (with --prefixes --output both) and:
    - Passes through kept blocks (+: prefix) unchanged
    - For consecutive cleared blocks: outputs first block in full, then only changes

    Diff mode (when enabled):
    - Green highlighting for additions
    - Red highlighting for deletions (and DL symbol)
    - Yellow highlighting for modifications
    """
    input_stream = input_file or sys.stdin

    # Create Rich console if diff is enabled
    # Force terminal mode to enable diffs even when piped
    console = Console(force_terminal=True) if diff else None

    # Initialize normalization engine and load sequence configurations
    # Create temporary rules file from tui_profiles.yaml
    module_dir = Path(__file__).parent
    profiles_path = module_dir / "tui_profiles.yaml"

    norm_engine: Optional[PatterndbYaml] = None  # type: ignore[valid-type]
    sequence_configs: dict[str, Any] = {}
    sequence_markers: set[str] = set()
    rules_path = None

    if profiles_path.exists():
        rules_path = _create_rules_file_from_profiles()
        norm_engine = PatterndbYaml(rules_path)
        # Extract sequence configurations from the engine
        sequence_configs = norm_engine.sequence_configs
        sequence_markers = norm_engine.sequence_markers

    in_cleared_sequence = False
    current_cleared_block: list[str] = []
    previous_cleared_block: list[str] = []
    current_prefix = ""

    # Choice buffering state
    buffered_choices: list[tuple[str, str]] = []  # List of (prefix, line) tuples

    try:
        for line in input_stream:
            line = line.rstrip("\n")
            line_type, content = parse_line(line)

            if line_type == LineType.COMMAND:
                # Output command line immediately without breaking cleared sequence
                # This allows consolidation to continue across command line boundaries
                print(line)
                continue

            if line_type == LineType.KEPT:
                # Before outputting kept line, finish any pending cleared block
                if in_cleared_sequence and current_cleared_block:
                    _flush_pending_cleared_block(
                        previous_cleared_block,
                        current_cleared_block,
                        current_prefix,
                        console,
                        diff,
                        norm_engine,
                        buffered_choices,
                        sequence_configs,
                        sequence_markers,
                    )

                    # End cleared sequence
                    in_cleared_sequence = False
                    previous_cleared_block = []
                    current_cleared_block = []

                # Output kept line
                print(line)

            else:  # Cleared line (backslash or slash)
                # Determine prefix for this cleared block
                if line_type == LineType.CLEARED_BACKSLASH:
                    new_prefix = "\\: "
                else:
                    new_prefix = "/: "

                # Check if this is a new cleared block (prefix changed)
                if in_cleared_sequence and new_prefix != current_prefix:
                    # Output previous cleared block
                    _flush_pending_cleared_block(
                        previous_cleared_block,
                        current_cleared_block,
                        current_prefix,
                        console,
                        diff,
                        norm_engine,
                        buffered_choices,
                        sequence_configs,
                        sequence_markers,
                    )

                    # Start new cleared block
                    previous_cleared_block = current_cleared_block
                    current_cleared_block = [content]
                    current_prefix = new_prefix
                else:
                    # Continue current cleared block
                    if not in_cleared_sequence:
                        in_cleared_sequence = True
                        current_prefix = new_prefix
                    current_cleared_block.append(content)

        # Handle any remaining cleared block at EOF
        if in_cleared_sequence and current_cleared_block:
            _flush_pending_cleared_block(
                previous_cleared_block,
                current_cleared_block,
                current_prefix,
                console,
                diff,
                norm_engine,
                buffered_choices,
                sequence_configs,
                sequence_markers,
            )

    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        sys.stderr.close()
    finally:
        # Clean up temporary rules file if created
        if rules_path and rules_path.exists():
            import os

            os.unlink(rules_path)


if __name__ == "__main__":
    app()
