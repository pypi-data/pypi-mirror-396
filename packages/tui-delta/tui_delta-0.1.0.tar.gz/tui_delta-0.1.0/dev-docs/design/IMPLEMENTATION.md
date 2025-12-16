# Implementation Overview

Internal implementation details for tui-delta developers.

**For user-facing documentation, see [README.md](../../README.md) and [docs/](../../docs/)**

## Architecture

### Component Structure

```
src/tui_delta/
    run.py              # Main execution: builds pipeline, manages processes
    clear_lines.py      # Stage 1: Detect and mark cleared lines
    consolidate_clears.py # Stage 2: Consolidate consecutive cleared blocks
    clear_rules.py      # YAML config loader for clear operation rules
    tui_profiles.yaml   # Profile configurations and pattern definitions
    cli.py              # Typer CLI interface
```

**Separation of Concerns**:
- Core processing modules are CLI-independent
- `run.py` builds and executes the subprocess pipeline
- `cli.py` handles argument parsing and user interface

## Processing Pipeline

**Pipeline stages** (implemented as chained subprocesses):

```
script | clear_lines | consolidate_clears | uniqseq | cut | [profile-specific]
```

1. **script**: Captures raw terminal output with ANSI sequences
2. **clear_lines**: Detects clear operations, marks lines with prefixes (+: kept, \\: /: cleared)
3. **consolidate_clears**: Outputs only deltas between consecutive cleared blocks
4. **uniqseq**: Deduplicates sequences (first stage - tracks prefixed lines)
5. **cut**: Strips the 4-character prefix added by clear_lines
6. **profile-specific**: Optional additional processing from profile config

**Why subprocess pipeline?**
- Real-time streaming with no buffering
- Each stage processes line-by-line
- Failure isolation - stages fail independently
- Unix philosophy - composable tools

## Core Algorithms

### Clear Line Detection (clear_lines.py)

Uses FIFO buffer to support lookahead/lookback:

1. Read lines into FIFO
2. When clear sequence detected (ESC[2K), apply clear rules
3. Rules determine how many lines to mark as cleared (N-1 baseline, with protections)
4. Output lines with state prefixes: `+: ` (kept), `\: ` or `/: ` (cleared, alternating)

**Key data structures**:
- `deque[tuple[int, str]]` - FIFO of (line_number, content)
- `ClearRules` - Loaded from YAML, evaluates protection conditions

### Clear Consolidation (consolidate_clears.py)

Tracks consecutive cleared blocks and outputs only changes:

1. First cleared block in sequence: output in full
2. Subsequent blocks: diff against previous, output only changes
3. Uses `difflib.SequenceMatcher` for line-level diffs
4. Extracts multi-line sequences (dialogs, choices) and buffers them
5. Outputs buffered sequences before first block without them

**Normalization**:
- Uses `patterndb-yaml` to normalize patterns before comparison
- Example: `[spinner-char:⠋]` → `[spinner-char:*]`
- Prevents spurious diffs from changing spinners/timestamps

**Sequence buffering**:
- Multi-line dialogs/choices extracted from cleared blocks
- Buffered until first block without them
- Ensures user sees prompts even if immediately cleared

## Configuration System

### Profiles (tui_profiles.yaml)

**Profile structure**:
```yaml
profiles:
  profile_name:
    description: "Profile description"
    clear_protections:      # Rules for clear_lines
      - protection_name
    additional_pipeline: "optional shell command"

clear_protections:
  protection_name:
    condition:
      type: "condition_type"
      pattern: "regex pattern"
    action:
      reduce_by: N  # or multiply_by, set_to

patterns:
  pattern_name:
    output: "[normalized-output]"
    pattern: [...]  # Pattern components
```

**Clear protections** modify clear count to prevent over-clearing:
- Example: Keep window title lines, dialog boundaries
- Evaluated in clear_lines based on line content

**Patterns** define normalization for consolidation:
- Spinner characters → generic marker
- Timestamps → generic placeholder
- Makes comparison ignore ephemeral changes

## Memory Management

**Bounded memory usage**:
- clear_lines: FIFO with configurable max size (default 100 lines)
- consolidate_clears: Buffers only current and previous cleared blocks
- Line-by-line streaming prevents unbounded growth

**Typical memory**: <10MB for normal sessions

## Error Handling

**Pipeline error behavior**:
- Each subprocess reports stderr independently
- First non-zero exit code becomes final exit code
- Broken pipe handled gracefully (downstream consumer exits)
- Partial output still reaches stdout before failure

## Platform Differences

**script command syntax**:
- macOS: `script -q -F /dev/stdout command`
- Linux: `script --flush --quiet --return --command "cmd" /dev/stdout`

Handled in `build_script_command()` (run.py:20)

## Dependencies

**External tools**:
- `script` - Terminal session recording (Unix standard utility)
- `syslog-ng` - Required by patterndb-yaml for pattern matching

**Python packages**:
- `typer` + `rich` - CLI framework with styled output
- `patterndb-yaml` - Pattern-based normalization engine
- `uniqseq` - Sequence deduplication
- `pyyaml` - Configuration parsing

## Testing Strategy

See [dev-docs/testing/](../testing/) for comprehensive testing documentation.

**Key approaches**:
- Property-based testing with Hypothesis
- Synthetic test data (no real session logs in tests)
- Fixture-based testing with known inputs/outputs
