# Library Usage

Using tui-delta as a Python library.

## Installation

```bash
pip install tui-delta
```

## Quick Start

```python
from tui_delta import run_tui_with_pipeline

# Run a TUI application with delta processing
exit_code = run_tui_with_pipeline(
    command=["echo", "Hello, World!"],
    profile="minimal"
)

print(f"Process exited with code: {exit_code}")
```

## Working with Profiles

```python
from tui_delta import ClearRules

# List available profiles
profiles = ClearRules.list_profiles()
for name, description in profiles.items():
    print(f"{name}: {description}")

# Load a specific profile
rules = ClearRules(profile="claude_code")

# Calculate clear count based on context
clear_count = rules.calculate_clear_count(
    clear_line_count=10,
    first_cleared_line="User input line",
    first_sequence_line="Initial prompt",
    next_line_after_clear=None
)
print(f"Will clear {clear_count} lines")
```

## See Also

- [API Reference](tui-delta.md) - Complete API reference
- [CLI Reference](cli.md) - Command-line interface
- [Custom Profiles](../guides/custom-profiles.md) - Creating custom profiles
