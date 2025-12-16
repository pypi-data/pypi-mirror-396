# Contributing to tui-delta

Thank you for your interest in contributing to tui-delta! This guide will help you get started.

## Ways to Contribute

### 1. Report Issues

Found a bug or have a feature request?

**Before creating an issue**:
- Search existing issues to avoid duplicates
- Check if it's already fixed in the main branch
- Gather relevant information (see below)

**What to include**:
```markdown
**Description**: Brief description of the issue

**Command used**:
```bash
tui-delta --something -- some-app
```

**Sample input** (first 20 lines):
```
[paste sample here]
```

**Expected behavior**: What you expected to happen

**Actual behavior**: What actually happened

**Environment**:
- tui-delta version: `tui-delta --version`
- Python version: `python --version`
- OS: macOS/Linux/Windows
```

### 2. Improve Documentation

Documentation improvements are always welcome!

**Types of documentation contributions**:
- Fix typos or unclear explanations
- Add examples for common use cases
- Improve existing guides
- Add new use case examples
- Clarify error messages

**Where documentation lives**:
- `docs/` - User-facing documentation (MkDocs)
- `README.md` - Project overview
- Code docstrings - API documentation

**Testing documentation changes**:
```bash
# Install dependencies
pip install -e ".[docs]"

# Serve documentation locally
mkdocs serve

# View at http://127.0.0.1:8000
```

### 3. Submit Code Changes

#### Getting Started

**Fork and clone**:
```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/processor.git
cd tui-delta-workspace/tui-delta
```

**Set up development environment**:
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

#### Code Standards

**Python code requirements**:

1. **Type hints** for all function signatures

2. **Docstrings** for public functions/classes

3. **Named constants** instead of magic numbers:
   ```python
   # Good
   DEFAULT_SOMETHING_SIZE = 10
   something_size = DEFAULT_SOMETHING_SIZE

   # Bad
   something_size = 10  # What does 10 mean?
   ```

4. **Code formatting**:
   ```bash
   # Format code (runs automatically via pre-commit)
   ruff format .

   # Check for issues
   ruff check .
   ```

5. **Type checking**:
   ```bash
   # Run type checker
   pyright
   ```

#### Testing Requirements

**All code changes must include tests.**

**Test categories**:
- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **Feature tests**: Test complete features with fixtures

#### Submitting Pull Requests

**Before submitting**:

1. **Create a branch**:
   ```bash
   git checkout -b feature/my-improvement
   ```

2. **Make your changes**:
   - Write code
   - Add tests
   - Update documentation
   - Ensure all tests pass

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

   **Good commit messages**:
   - Start with verb (Add, Fix, Update, Remove)
   - Keep first line under 50 characters
   - Add detailed description if needed

4. **Push and create PR**:
   ```bash
   git push origin feature/my-improvement
   ```

   Then create a Pull Request on GitHub.

**PR description should include**:
- What problem does this solve?
- How does it solve it?
- Any breaking changes?
- Related issues (closes #123)

**PR checklist**:
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Pre-commit hooks pass
- [ ] No merge conflicts

## Development Workflow

### Project Structure

```
tui-delta/
├── src/tui_delta/          # Source code
│   ├── __init__.py
│   ├── cli.py            # CLI interface (Typer)
│   ├── clear_lines.py    # Clear detection
│   └── ...
├── tests/                # Test files
│   ├── test_clear_lines.py
│   ├── test_consolidate_clears.py
│   └── fixtures/         # Test data files
├── docs/                 # Documentation (MkDocs)
│   ├── guides/
│   ├── features/
│   └── use-cases/
├── pyproject.toml        # Project configuration
└── README.md
```

### Running Quality Checks

**Before committing** (automatic via pre-commit):
```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
pyright

# Run tests
pytest
```

**All checks together**:
```bash
# Run pre-commit on all files
pre-commit run --all-files
```

### Building Documentation

**Local preview**:
```bash
# Install docs dependencies
pip install -e ".[docs]"

# Serve documentation
mkdocs serve

# Open http://127.0.0.1:8000
```

**Build static site**:
```bash
mkdocs build
# Output in site/
```

### Debugging

**Enable debug logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Use pytest debugger**:
```bash
# Drop into debugger on failure
pytest --pdb

# Start debugger at specific test
pytest tests/test_file.py::test_function --pdb
```

**Profile performance**:
```bash
# Time a command
time tui-delta large-file.log > /dev/null

# Profile with cProfile
python -m cProfile -s cumulative -m tui-delta large-file.log
```

## Feature Development Guidelines

### Adding a New Feature

**Process**:

1. **Discuss first**: Open an issue to discuss the feature
2. **Design**: Write design doc if complex
3. **Implement**: Write code + tests
4. **Document**: Add to user documentation
5. **Submit**: Create PR

### Code Review Process

**What reviewers look for**:

- Does code work correctly?
- Are tests comprehensive?
- Is code readable and maintainable?
- Is documentation clear?
- Are edge cases handled?

**Responding to feedback**:
- Be open to suggestions
- Ask questions if unclear
- Make requested changes
- Push updates to same branch

## Common Development Tasks

### Adding Documentation

```bash
# Create new doc page
mkdir -p docs/features/my-feature
touch docs/features/my-feature/my-feature.md

# Add to navigation (mkdocs.yml)
# Edit nav: section

# Preview
mkdocs serve
```

### Updating Dependencies

```bash
# Update specific package
pip install --upgrade package-name

# Update all dev dependencies
pip install --upgrade -e ".[dev]"

# Regenerate lockfile (if using)
pip freeze > requirements.txt
```

## Getting Help

### Resources

- **Documentation**: https://github.com/JeffreyUrban/tui-delta/docs
- **Issue Tracker**: https://github.com/JeffreyUrban/tui-delta/issues
- **Discussions**: https://github.com/JeffreyUrban/tui-delta/discussions

### Ask Questions

**Where to ask**:
- GitHub Discussions for general questions
- GitHub Issues for bugs/features
- PR comments for code-specific questions

**How to ask**:
- Be specific about what you're trying to do
- Include code snippets or examples
- Show what you've already tried

## Code of Conduct

**Be respectful and inclusive**:
- Welcome newcomers
- Be patient with questions
- Provide constructive feedback
- Focus on the code, not the person

**Unacceptable behavior**:
- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Other unprofessional conduct

## License

By contributing to tui-delta, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes for significant contributions
- Documentation credits for major doc improvements

Thank you for contributing to tui-delta! 🎉
