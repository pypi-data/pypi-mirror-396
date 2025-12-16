#!/usr/bin/env python3
"""Generate golden output file from real Claude Code session.

Runs the pipeline directly (without script wrapper) to generate expected output.
"""

import subprocess
import sys
from pathlib import Path

# Paths
FIXTURES_DIR = Path(__file__).parent / "fixtures"
REAL_CLAUDE_SESSION = FIXTURES_DIR / "real-claude-session.bin"
GOLDEN_OUTPUT = FIXTURES_DIR / "real-claude-session-expected.txt"

# Read fixture data
fixture_data = REAL_CLAUDE_SESSION.read_bytes()

print(f"Input size: {len(fixture_data):,} bytes", file=sys.stderr)

# Build pipeline (matching run.py's build_pipeline_commands for claude_code profile)
# Stage 1: clear_lines
clear_lines_proc = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "tui_delta.clear_lines",
        "--prefixes",
        "--profile",
        "claude_code",
    ],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

# Stage 2: consolidate_clears
consolidate_proc = subprocess.Popen(
    [sys.executable, "-m", "tui_delta.consolidate_clears"],
    stdin=clear_lines_proc.stdout,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
clear_lines_proc.stdout.close()

# Stage 3: first uniqseq
uniqseq1_proc = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "uniqseq",
        "--track",
        r"^\+: ",
        "--quiet",
    ],
    stdin=consolidate_proc.stdout,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
consolidate_proc.stdout.close()

# Stage 4: cut -b 4- (strip prefix)
cut_proc = subprocess.Popen(
    [sys.executable, "-c", "import sys; [print(line[3:], end='') for line in sys.stdin]"],
    stdin=uniqseq1_proc.stdout,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
uniqseq1_proc.stdout.close()

# Stage 5: final uniqseq (from claude_code profile)
uniqseq2_proc = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "uniqseq",
        "--track",
        r"^\S",
        "--quiet",
        "--max-history",
        "5",
        "--window-size",
        "1",
        "--max-unique-sequences",
        "0",
    ],
    stdin=cut_proc.stdout,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
cut_proc.stdout.close()

# Feed input
try:
    clear_lines_proc.stdin.write(fixture_data)
    clear_lines_proc.stdin.close()
except BrokenPipeError:
    print("Broken pipe when writing to clear_lines", file=sys.stderr)
    # Collect errors from all processes
    for name, proc in [
        ("clear_lines", clear_lines_proc),
        ("consolidate", consolidate_proc),
        ("uniqseq1", uniqseq1_proc),
        ("cut", cut_proc),
        ("uniqseq2", uniqseq2_proc),
    ]:
        proc.wait()
        if proc.returncode != 0:
            _, stderr = proc.communicate()
            print(f"{name} failed with code {proc.returncode}: {stderr.decode()}", file=sys.stderr)
    sys.exit(1)

# Collect output
output, errors = uniqseq2_proc.communicate()

# Check for errors
if uniqseq2_proc.returncode != 0:
    print(f"Pipeline failed: {errors.decode()}", file=sys.stderr)
    sys.exit(1)

# Write golden output
GOLDEN_OUTPUT.write_bytes(output)

print(f"Golden output generated: {GOLDEN_OUTPUT}")
print(f"Output size: {len(output):,} bytes")
print(f"Output lines: {len(output.decode('utf-8', errors='replace').splitlines()):,}")
print(f"Compression: {100 * (1 - len(output) / len(fixture_data)):.1f}%")
