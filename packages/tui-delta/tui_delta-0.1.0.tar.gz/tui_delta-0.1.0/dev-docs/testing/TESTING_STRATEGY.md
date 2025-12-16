# Testing Strategy

## Test Data Philosophy

**All tests use synthetic data** - no real TUI session logs

**Rationale**:
- **Reproducibility**: Synthetic patterns are deterministic
- **Clarity**: Test intent is obvious from data generation
- **Compactness**: Minimal test data for specific scenarios
- **Privacy**: No risk of exposing sensitive session content

**Example pattern**
```python
# Generate test input with clear sequences
lines = ["line1\n", "line2\n", "update\x1b[2K\x1b[2K\n"]
```

### tests/test_tui-delta.py

**Purpose**: Comprehensive test suite

**Test organization**:
- Basic functionality tests
- Edge case tests
- Configuration tests
- Advanced tests
- Performance tests

**All tests use StringIO for output** - no file I/O in tests
