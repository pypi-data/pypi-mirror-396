# Design Rationale

Key design decisions and trade-offs for tui-delta.

**For implementation details, see [IMPLEMENTATION.md](IMPLEMENTATION.md)**

## Core Design Principles

### 1. Preserve All Meaningful Content

**Principle**: Never discard content that the user saw, even briefly.

**Implementation**:
- Cleared blocks output in full on first occurrence
- Subsequent blocks output deltas (what changed)
- Ephemeral content (spinners, progress) preserved in logs

**Trade-off**: Larger log files vs simpler "final state only" approaches. Chose completeness over brevity.

### 2. Real-time Streaming

**Principle**: No buffering delays - output available immediately.

**Implementation**:
- Line-by-line processing throughout pipeline
- Subprocess pipeline with pipes (not temporary files)
- Flush after each line

**Trade-off**: Cannot look arbitrarily far ahead. Chose responsiveness over perfect deduplication.

### 3. Unix Pipeline Architecture

**Principle**: Composable tools, each doing one thing well.

**Why subprocess pipeline vs monolithic Python**:
- ✅ Each stage testable independently
- ✅ Failures isolated (one stage fails, others continue)
- ✅ Natural streaming with OS pipe buffers
- ✅ Can replace stages (e.g., different uniqseq implementation)
- ❌ Slight overhead from process spawning (negligible for long-running sessions)

**Alternative considered**: Single Python process with internal pipeline. Rejected due to tight coupling and harder testing.

## Algorithm Choices

### Clear Detection: N-1 Formula

**Decision**: Clear `N-1` lines where N = count of clear sequences.

**Rationale**:
- TUI apps typically emit N clear sequences when updating N lines
- The Nth clear is for the current line (not yet displayed)
- Previous N-1 lines are the ones being replaced

**Protection rules**: Handle edge cases where N-1 is wrong (window titles, dialog boundaries).

### Consolidation: Diff vs Full Output

**Decision**: First block in full, subsequent blocks show only changes.

**Rationale**:
- User must see initial state to understand context
- Subsequent blocks usually small changes (spinner updates, progress ticks)
- Diff output dramatically reduces redundancy

**Alternative considered**: Always output full blocks. Rejected due to excessive redundancy.

### Normalization Before Comparison

**Decision**: Normalize patterns (spinners, timestamps) before diffing.

**Rationale**:
- Spinner characters change constantly but aren't meaningful differences
- Timestamp updates aren't content changes
- Without normalization, every spinner tick generates output

**Implementation**: patterndb-yaml with YAML pattern definitions.

## Configuration System

### YAML Profiles

**Decision**: Profile-based configuration in YAML.

**Why YAML over**:
- JSON: YAML supports comments, more human-friendly for config
- Python code: YAML is safer, doesn't require code execution
- Command-line flags: Too many options, profiles group related settings

**Profile hierarchy**:
- `claude_code` - Full processing for Claude Code
- `generic` - Universal rules for any TUI
- `minimal` - Barely any processing (baseline)

### Separation: Clear Rules vs Patterns

**Decision**: Separate YAML sections for clear protections and normalization patterns.

**Rationale**:
- Clear protections: Affect what gets cleared (clear_lines stage)
- Patterns: Affect comparison (consolidation stage)
- Different purposes, different stages - keep separate

## Dependency Choices

### Why patterndb-yaml?

**Decision**: Use patterndb-yaml for pattern matching.

**Alternatives considered**:
- Regex: Too complex for multi-line patterns with alternatives
- Custom DSL: Reinventing the wheel
- patterndb-yaml: Mature, handles complex patterns, already exists

**Trade-off**: Adds syslog-ng dependency. Worth it for powerful pattern matching.

### Why uniqseq?

**Decision**: Use uniqseq for sequence deduplication.

**Rationale**:
- Needed sequence tracking (not just line dedup)
- uniqseq already existed for this purpose
- Maintains focus: tui-delta = TUI capture + processing, uniqseq = dedup

## Output Format Choices

### State Prefixes (+: \: /:)

**Decision**: Use 3-character prefixes to mark line states.

**Rationale**:
- Makes clear detection visible for debugging
- Enables consolidation to distinguish block boundaries
- Stripped before final output (via cut)

**Why two cleared prefixes** (\\ and /):
- Alternating prefixes show clear operation boundaries
- Helps debugging: can see which lines belong to same clear operation

## Scope Decisions

### What tui-delta IS

- TUI capture and delta processing
- Profile-based configuration
- Real-time streaming output
- Content preservation

### What tui-delta is NOT

- Session replay tool (use asciinema)
- Log analyzer (use grep, awk, etc.)
- TUI framework (use rich, textual)
- General log processor (use standard Unix tools)

**Principle**: Focus on TUI capture/processing, delegate other concerns to existing tools.
