# Algorithm Design

Detailed algorithm specifications for core processing stages.

**For implementation details, see [IMPLEMENTATION.md](IMPLEMENTATION.md)**

## Clear Detection Algorithm

**Goal**: Identify which lines were cleared/overwritten by the TUI application.

### Input Processing

```python
# Input: Lines with ANSI clear sequences
line = "Some content\x1b[2K\x1b[2K"  # 2 clear sequences
clear_count = line.count("\x1b[2K")  # N = 2
```

### Clear Count Calculation

**Baseline formula**: Clear `N - 1` lines

- If line has 2 clear sequences → clear 1 line
- If line has 5 clear sequences → clear 4 lines

**Rationale**: Clear sequence count indicates how many lines the TUI updated, including the current line. We clear previous lines but keep the current one.

### Protection Rules

Rules modify the baseline clear count to prevent incorrect clearing:

**Condition types**:
- `first_cleared_line_matches`: Check first line that would be cleared
- `first_sequence_line_matches`: Check first line of current sequence
- `next_line_matches`: Check line immediately after clear

**Actions**:
- `reduce_by: N` - Reduce clear count by N
- `multiply_by: F` - Multiply clear count by factor F
- `set_to: N` - Set clear count to specific value N

**Example** (keep window title):
```yaml
condition:
  type: first_cleared_line_matches
  pattern: '^\[window-title:'
action:
  reduce_by: 1  # Don't clear the window title line
```

### FIFO Buffer

Uses `deque` for efficient lookahead/lookback:

```
Upstream →  [old_line, line2, line3, current_line, clear_line]  → Downstream
           Front/Left                               Back/Right
           (output)                                 (input)
```

**Operations**:
- `append(line)` - Add new line (right/upstream)
- `popleft()` - Remove for output (left/downstream)
- Maintains insertion order for correct line sequence

## Consolidation Algorithm

**Goal**: Output only changes between consecutive cleared blocks.

### State Machine

```
State: NOT_IN_CLEARED_SEQUENCE
  On kept line (+:) → output, stay
  On cleared line (\:) → enter CLEARED_SEQUENCE, buffer line

State: CLEARED_SEQUENCE
  On kept line (+:) → flush buffer, output line, exit to NOT_IN_CLEARED
  On same prefix (\: or /:) → buffer line, stay
  On different prefix → flush buffer with diff, start new buffer
```

### Diff Algorithm

Uses `difflib.SequenceMatcher` for line-level comparison:

```python
matcher = SequenceMatcher(None, prev_normalized, curr_normalized)
for tag, i1, i2, j1, j2 in matcher.get_opcodes():
    if tag == 'equal': skip
    elif tag == 'insert': output curr_lines[j1:j2]
    elif tag == 'replace': output curr_lines[j1:j2]
    elif tag == 'delete': skip (already output in previous block)
```

**Normalized comparison**:
- Lines normalized via patterndb-yaml before comparison
- Example: Different spinner chars all normalize to same pattern
- Comparison sees them as equal, so no output

### Sequence Buffering

**Multi-line patterns** (dialogs, choice menus):
1. Extract sequences from cleared blocks using pattern matching
2. Buffer extracted sequences
3. Output buffered sequences before first block without them
4. Clear buffer when new sequences appear

**Rationale**: User must see prompts/dialogs even if TUI clears them immediately.

## Pattern Matching (via patterndb-yaml)

**Component matching**:
- `text`: Fixed string literal
- `serialized`: Literal characters (e.g., newline)
- `field`: Variable content with parser (NUMBER, etc.)
- `alternatives`: Match any of several alternatives

**Example pattern**:
```yaml
pattern:
  - text: "[spinner-char:"
  - alternatives:
      - [text: "⠋"]
      - [text: "⠙"]
      - [text: "⠹"]
      # ... all spinner variants
  - text: "]"
output: "[spinner-char:*]"
```

All spinner variations normalize to `[spinner-char:*]`.

## Performance Characteristics

**Time complexity**:
- Clear detection: O(n) where n = input lines
- Consolidation: O(n × m) where m = avg cleared block size
- Pattern matching: O(n × p) where p = patterns checked per line

**Space complexity**:
- Clear lines: O(buffer_size) - bounded by FIFO max
- Consolidation: O(max_block_size × 2) - current + previous blocks
- Overall: O(1) constant memory for streaming

**Streaming property**: Line output happens as soon as it's determined to be final (no future buffering needed).
