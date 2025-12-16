# Test Coverage

## Overview

Test coverage for tui-delta pipeline components. Tests are organized into three categories:

1. **Unit Tests**: Targeted tests for specific components and edge cases
2. **Property Tests**: Tests verifying invariants hold under all conditions
3. **Integration Tests**: End-to-end pipeline tests with realistic data

All tests use **pytest exclusively** (not unittest).

## Test Philosophy

- **Component-focused**: Test individual pipeline components (clear_lines, consolidate_clears, clear_rules)
- **Comprehensive edge cases**: Exercise boundary conditions and error paths
- **Invariant verification**: Ensure algorithm guarantees hold
- **Integration validation**: Golden output test ensures end-to-end correctness
- **Clear test names**: Describe what's being tested and expected behavior

## 1. Unit Tests

### 1.1 Edge Cases (`tests/test_edge_cases.py`)

Tests edge cases and boundary conditions for pipeline components.

**TestClearLinesEdgeCases:**
- Empty input handling
- Single clear with no lines to clear
- Clear sequence counting (empty, single, multiple)
- Line formatting options (prefixes, line numbers)
- Clear count formula validation (N-1)
- Protection rules (blank boundary)

**TestClearRulesEdgeCases:**
- Non-existent profile handling
- Profile configurations (minimal, generic, claude_code)
- Profile listing
- Zero clear count handling

**TestConsolidateEdgeCases:**
- Line prefix parsing (+:, \\:, /:, >:)
- Window title detection

### 1.2 Comprehensive Tests (`tests/test_comprehensive.py`)

Tests using precomputed fixture cases.

**TestHandcraftedCases:**
- Simple clear operations
- Blank boundary protection

**TestEdgeCases:**
- Single line inputs
- Excessive clear sequences

**TestRandomCases:**
- Mixed content with multiple clear operations

**TestInvariantsWithFixtures:**
- No data loss verification
- Line order preservation

**TestFixtureQuality:**
- Fixture loading validation
- Required fields verification
- Profile validation

## 2. Property-Based Tests

### 2.1 Invariant Testing (`tests/test_invariants.py`)

Tests that algorithm invariants hold under all conditions.

**TestClearLinesInvariants:**
- Clear count never exceeds available lines
- FIFO order preservation
- Kept line prefix (+:) verification

**TestPipelineInvariants:**
- Pipeline output size bounded (compression, not expansion)
- Line count preservation or reduction (no line creation)

**TestClearRulesInvariants:**
- Calculated count bounded by input (N-1)
- Protections only reduce count (never increase)

## 3. Integration Tests

### 3.1 Pipeline Integration (`tests/test_integration.py`)

End-to-end pipeline tests.

**TestClaudeCodePipeline:**
- Pipeline command structure validation
- Full pipeline execution with `run_tui_with_pipeline`
- Golden output verification (byte-for-byte match)
- Profile-specific testing (claude_code, generic)

## 4. CLI Tests

### 4.1 CLI Interface (`tests/test_cli.py`)

Tests for command-line interface.

- Help display
- File and stdin input
- Empty input handling
- Statistics output
- Quiet mode
- Progress indicators
- JSON stats format
- Error handling

## 5. Test Markers

```python
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests for specific components",
    "property: Property-based tests with invariant checking",
    "integration: End-to-end integration tests",
    "slow: Tests that take >1 second",
]
```

## 6. Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest -m unit

# Run only fast tests (exclude slow)
pytest -m "not slow"

# Run specific test file
pytest tests/test_edge_cases.py

# Run with coverage
pytest --cov=tui_delta --cov-report=html

# Run in parallel (requires pytest-xdist)
pytest -n auto

# Verbose output
pytest -v
```

## 7. Test Fixtures

### 7.1 Fixture Files (`tests/fixtures/`)

**handcrafted_cases.json**: Manually crafted test cases with known patterns
**edge_cases.json**: Boundary condition cases
**random_cases.json**: Mixed content scenarios

Each fixture includes:
- `name`: Test case identifier
- `description`: Human-readable description
- `input_lines`: Input data
- `expected_output_count`: Expected number of output lines
- `profile`: Profile to use (minimal, generic, claude_code)

### 7.2 Shared Fixtures (`tests/conftest.py`)

- `temp_dir`: Temporary directory for test files

## 8. Coverage Goals

**Target: 90%+ line coverage for core components**

**Core components:**
- `clear_lines.py`: Line detection and marking
- `consolidate_clears.py`: Block consolidation
- `clear_rules.py`: Rule configuration and evaluation
- `run.py`: Pipeline orchestration

**Not requiring full coverage:**
- `cli.py`: CLI interface (tested via integration)
- `tui_delta.py`: Template placeholder (not used)

## 9. Test Execution Strategy

### 9.1 Development Workflow

```bash
# Quick validation during development
pytest -m unit --tb=short

# Full validation before commit
pytest

# Coverage check
pytest --cov=tui_delta --cov-report=term-missing
```

### 9.2 CI/CD Pipeline

```bash
# Fast feedback
pytest -m "unit and not slow"

# Full test suite
pytest --cov=tui_delta --cov-report=xml
```

## 10. Current Test Count

**Total:** 47 tests adapted for tui-delta components
- Unit tests: 22 (edge cases)
- Property tests: 7 (invariants)
- Comprehensive tests: 15 (fixtures)
- Integration tests: 3 (pipeline)

**Coverage areas:**
- ✅ clear_lines module
- ✅ clear_rules module
- ✅ consolidate_clears module (basic)
- ✅ Pipeline integration
- ✅ CLI interface
- ⚠️ Consolidate normalization patterns (needs expansion)

## 11. Future Test Additions

**High priority:**
- Consolidate normalization pattern tests
- Profile-specific pattern matching tests
- Error propagation in pipeline
- Custom profile YAML validation

**Medium priority:**
- Performance benchmarks
- Memory usage validation
- Large file handling
- Unicode and special character handling

**Low priority:**
- Documentation example validation
- MkDocs build testing (already exists)
