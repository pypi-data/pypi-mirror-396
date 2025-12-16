# Custom Profiles

Create custom profiles for your TUI applications.

## Profile Structure

Profiles are defined in YAML files with three main sections:

```yaml
profiles:
  my_profile:
    description: "My TUI application"
    clear_protections:
      - blank_boundary
    normalization_patterns:
      - my_pattern
    additional_pipeline: "uniqseq --track '^\\S' --quiet"
```

## Creating a Custom Profile

### 1. Create a YAML File

Create `my-profiles.yaml` with a custom profile:

```yaml
profiles:
  test_profile:
    description: "Test profile"
    clear_protections:
      - blank_boundary
    normalization_patterns: []
```

### 2. Use with `--rules-file`

Pass the custom profile file with `--rules-file`:

```bash
tui-delta run --rules-file my-profiles.yaml --profile test_profile -- <command>
```

## Profile Fields

### `description`

Human-readable description shown in `list-profiles`.

### `clear_protections`

List of protection rules to apply. Available protections:

- **`blank_boundary`** - Preserve blank lines at clear boundaries
- **`user_input_final`** - Preserve final user input (Claude Code specific)

Start with `blank_boundary` for most TUI apps.

### `normalization_patterns`

List of pattern names to normalize during consolidation. Patterns make lines with varying details (timestamps, spinners) compare as equal.

For most TUIs, start with empty list `[]`.

### `additional_pipeline`

Optional shell command for final processing. Common use:

```yaml
additional_pipeline: "uniqseq --track '^\\S' --quiet"
```

This adds a final deduplication stage.

## Example: Starting from Generic

Copy the `generic` profile as a template:

```yaml
profiles:
  my_custom:
    description: "My custom profile"
    clear_protections:
      - blank_boundary
    normalization_patterns: []
```

## Defining Patterns (Advanced)

Normalization patterns define how to recognize and normalize lines. Example:

```yaml
patterns:
  my_spinner:
    description: "Spinner with rotating symbols"
    pattern:
      - char: "·✢✳✶✻✽"  # Matches any of these symbols
      - text: " "
      - field: task
      - text: "…"
    output: "[spinner:{task}]"
```

This normalizes all spinner variations to `[spinner:task_name]` for comparison.

The `normalization_patterns` section uses [patterndb-yaml](https://patterndb-yaml.readthedocs.io/)'s YAML format for pattern definitions. See the [patterndb-yaml Rules Documentation](https://patterndb-yaml.readthedocs.io/en/latest/features/rules/rules/) for pattern syntax details. Reference the [built-in profiles](https://github.com/JeffreyUrban/tui-delta/blob/main/src/tui_delta/tui_profiles.yaml) for complete tui-delta profile examples.

## Testing Your Profile

<!-- interactive-only -->
Test on your actual TUI application:

```console
$ tui-delta run --rules-file my-profile.yaml --profile my_custom \
  -- ./myapp | less -R
```

Check output looks correct and adjust protections or patterns as needed.

For AI assistants like Claude Code, see [AI Assistant Logging](../use-cases/ai-assistants/ai-assistants.md).

## Next Steps

- **[CLI Reference](../reference/cli.md)** - Command options
- **[Built-in Profiles](https://github.com/JeffreyUrban/tui-delta/blob/main/src/tui_delta/tui_profiles.yaml)** - Complete tui-delta profile examples
- **[patterndb-yaml Rules](https://patterndb-yaml.readthedocs.io/en/latest/features/rules/rules/)** - Pattern syntax for normalization_patterns section
