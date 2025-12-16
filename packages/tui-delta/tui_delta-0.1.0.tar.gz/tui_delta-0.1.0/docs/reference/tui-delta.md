# tui-delta API

API reference for tui-delta's core programmatic interfaces.

## Overview

tui-delta provides two main APIs for programmatic use:

- **`run_tui_with_pipeline()`** - Run TUI applications with delta processing
- **`ClearRules`** - Manage clear rules and profiles

These APIs enable integration of tui-delta's delta processing into Python applications.

## run_tui_with_pipeline()

::: tui_delta.run.run_tui_with_pipeline
    options:
      show_source: false
      show_root_heading: false
      heading_level: 3

## ClearRules

::: tui_delta.clear_rules.ClearRules
    options:
      show_source: false
      show_root_heading: false
      heading_level: 3

## Basic Usage

### Running TUI Applications

```python
from tui_delta import run_tui_with_pipeline

# Run with default profile (generic)
exit_code = run_tui_with_pipeline(
    command=["echo", "Hello, World!"]
)

# Run with specific profile
exit_code = run_tui_with_pipeline(
    command=["npm", "test"],
    profile="claude_code"
)

# Run with custom rules file
from pathlib import Path

exit_code = run_tui_with_pipeline(
    command=["./myapp"],
    rules_file=Path("custom-rules.yaml")
)
```

### Working with Profiles

```python
from tui_delta import ClearRules

# List all available profiles
profiles = ClearRules.list_profiles()
for name, description in profiles.items():
    print(f"{name}: {description}")

# Output:
# claude_code: Claude Code terminal UI (claude.ai/code)
# generic: Generic TUI with only universal rules
# minimal: Minimal - only base rule, no protections
```

### Loading Profile Configuration

```python
from tui_delta import ClearRules

# Load default profile (generic)
rules = ClearRules()

# Load specific profile
rules = ClearRules(profile="claude_code")

# Load from custom file
from pathlib import Path
rules = ClearRules(
    config_path=Path("custom-rules.yaml"),
    profile="my_profile"
)
```

### Calculating Clear Counts

```python
from tui_delta import ClearRules

rules = ClearRules(profile="claude_code")

# Calculate clear count based on line context
clear_count = rules.calculate_clear_count(
    clear_line_count=10,
    first_cleared_line="",  # Blank boundary
    first_sequence_line="User: What is the status?",
    next_line_after_clear="User: Another question"
)

print(f"Will clear {clear_count} lines")
# Output depends on profile rules and line content
# Base: 10 - 1 = 9 lines
# Protections may reduce further based on patterns
```

## Advanced Usage

### Custom Profile Management

```python
from tui_delta import ClearRules
from pathlib import Path

# Load custom rules file
rules_file = Path("my-app-rules.yaml")
rules = ClearRules(
    config_path=rules_file,
    profile="my_app"
)

# Get profile configuration
config = ClearRules.get_profile_config(
    profile="my_app",
    config_path=rules_file
)

print(f"Clear protections: {config['clear_protections']}")
print(f"Normalization patterns: {config['normalization_patterns']}")
print(f"Additional pipeline: {config.get('additional_pipeline', 'None')}")
```

### Subprocess Integration

```python
import subprocess
from pathlib import Path

# Run tui-delta as subprocess for maximum control
result = subprocess.run(
    ["tui-delta", "run", "--profile", "claude_code", "--", "echo", "test"],
    capture_output=True,
    text=True
)

print(f"Exit code: {result.returncode}")
print(f"Output:\n{result.stdout}")
```

### Stream Processing

While tui-delta's primary design uses subprocess pipelines, you can access individual processing stages programmatically:

```python
import sys
from pathlib import Path

# Process using clear_lines module
from tui_delta.clear_lines import clear_lines

with open("input.bin", "rb") as infile:
    for line in clear_lines(
        infile,
        profile="claude_code",
        add_prefix=True
    ):
        sys.stdout.buffer.write(line)
```

**Note**: For most use cases, `run_tui_with_pipeline()` is recommended as it manages the complete pipeline correctly.

## Profile System

### Built-in Profiles

tui-delta includes three built-in profiles:

**claude_code**
- Clear protections: `blank_boundary`, `user_input_final`
- Normalization patterns: 8 patterns for Claude Code UI elements
- Additional pipeline: Advanced deduplication with uniqseq
- Best for: Claude Code AI assistant sessions

**generic**
- Clear protections: `blank_boundary` only
- Normalization patterns: None
- Additional pipeline: Basic deduplication
- Best for: Most TUI applications

**minimal**
- Clear protections: None
- Normalization patterns: None
- Additional pipeline: None
- Best for: Debugging, minimal processing

### Profile Configuration

Profiles are defined in YAML format:

```yaml
profiles:
  my_profile:
    description: "My custom TUI application"
    clear_protections:
      - blank_boundary
      - user_input_final
    normalization_patterns:
      - pattern_name_1
      - pattern_name_2
    additional_pipeline: "uniqseq --quiet"
```

See [Custom Profiles Guide](../guides/custom-profiles.md) for detailed configuration.

## Error Handling

```python
from tui_delta import run_tui_with_pipeline
import sys

exit_code = run_tui_with_pipeline(
    command=["nonexistent-command"],
    profile="claude_code"
)

if exit_code != 0:
    print(f"Command failed with exit code {exit_code}", file=sys.stderr)
    sys.exit(exit_code)
```

Pipeline errors are automatically reported to stderr with stage identification and full error details.

## See Also

- [CLI Reference](cli.md) - Command-line interface
- [Library Usage](library.md) - Quick start guide
- [Custom Profiles](../guides/custom-profiles.md) - Creating profiles
- [Basic Concepts](../getting-started/basic-concepts.md) - How tui-delta works
