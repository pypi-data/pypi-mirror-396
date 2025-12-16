# Release Workflow

Step-by-step workflow for preparing and creating releases.

**Inherits from:** [../../CLAUDE.md](../../CLAUDE.md) - Read universal rules first

---

## When User Asks to Prepare for Release

**You should know exactly what to do.** Follow this workflow without asking.

---

## Release Preparation Workflow

### 1. Check Project-Specific Prerequisites

**REQUIRED: Check deployment prerequisites in [dev-docs/deployment/DEPLOYMENT.md](../../dev-docs/deployment/DEPLOYMENT.md)**

Current prerequisites for this project:
- Full Python test matrix enabled in `.github/workflows/test.yml`
- Python version tests added to branch protection required checks
- Coverage requirement `--cov-fail-under` set to appropriate level (not 0)

### 2. Create Release Preparation Branch

**All release preparation must go through a PR, not direct push to main.**

```bash
git checkout -b release/vX.Y.Z
```

### 3. Run Pre-commit Checks

```bash
pre-commit run --all-files
```

All checks must pass. If they don't, you're blocked - fix issues before proceeding.

### 4. Update CHANGELOG.md

**This project maintains CHANGELOG.md - it must be updated for every release.**

Add release section with **today's date** (from `<env>` tag):

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Feature description (factual, technical language)

### Changed
- Changed behavior description

### Fixed
- Bug fix description

### Removed
- Removed feature description
```

**Style guidelines:**
- Use factual, technical language
- Avoid marketing terms ("New!", "Exciting!", "Amazing!")
- State what changed, not why it's great
- Be concise and specific

**Remove placeholder content:**
- Remove `TEMPLATE_PLACEHOLDER` entries
- Update the `[0.0.0] - 1970-01-01` placeholder section

### 5. Update README.md (First Release Only)

**For v0.1.0 and initial releases:**
- Remove "Early Development - Not Ready for Use" warning section
- Update any "not ready" or "coming soon" language
- Ensure installation instructions are current

### 6. Clean Up Template Artifacts

**CRITICAL: Must be thorough - search entire codebase.**

**Process:**

1. **Find ALL TEMPLATE_PLACEHOLDER and cookiecutter instances:**
   ```bash
   grep -r "TEMPLATE_PLACEHOLDER" . --exclude-dir=.git --exclude-dir=.venv
   grep -r "cookiecutter" . --exclude-dir=.git --exclude-dir=.venv
   ```

2. **Review each instance and either:**
   - Replace with actual content (dev-docs, templates)
   - Remove the file if it's unused
   - Verify it's intentional test data or code (e.g., variable names in tests)

3. **Populate dev-docs with concise, non-redundant content:**
   - **Check dev-docs/** files for TEMPLATE_PLACEHOLDER entries
   - **Populate with internal/developer information** that's NOT in README or docs/
   - **Keep concise and basic** - focus on architecture, algorithms, design decisions
   - **Don't repeat** user-facing documentation - link to it instead
   - **Guidance**: dev-docs are for internal implementation details, not user guides

4. **Remove documentation for unimplemented features:**
   - Search for references to unimplemented features (e.g., `oracle`, `fixture generation`)
   - Check if implementation exists (e.g., does `tests/oracle.py` exist?)
   - If not implemented: remove the documentation file and all references to it
   - Search common patterns:
     ```bash
     # Find feature-specific docs that might be unimplemented
     grep -r "oracle\|generator\|placeholder" dev-docs/ --exclude-dir=.git -i
     ```
   - Update all cross-references in CLAUDE.md, README files, and .claude/ docs

5. **Find unused test fixtures:**
   ```bash
   # List all fixture files
   find tests/fixtures -type f

   # Search for usage of each fixture file in test code
   grep -r "fixture-name" tests/
   ```

6. **Remove any files that are:**
   - Template placeholders never filled in
   - Test fixtures not referenced by any tests
   - TODO/WIP files that should be completed or removed

**Don't skip this step or do it superficially - every TEMPLATE_PLACEHOLDER must be addressed.**

### 7. Update Documentation

**Ensure all documentation is current:**
- README.md reflects current state
- API documentation is complete
- Examples work with current code

### 8. Commit and Push Release Prep

```bash
git add .
git commit -m "chore: prepare release vX.Y.Z"
git push origin release/vX.Y.Z
```

### 9. Create Pull Request

Create PR for release preparation:
- Title: `chore: prepare release vX.Y.Z`
- Description: Summary of changes in this release

**Stop here.** User will review, approve, and merge the PR.

---

## Release Workflow (After User Merges Release Prep PR)

### 1. Ensure Main Branch is Up to Date

```bash
git checkout main
git pull
```

### 2. Create Release Tag

**Version is automatically determined by git tags via `hatch-vcs`.**

```bash
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push origin vX.Y.Z
```

### 3. Create GitHub Release

**Recommended: Use GitHub UI**

- Go to: https://github.com/JeffreyUrban/tui-delta/releases/new
- Tag: Select `vX.Y.Z` (just created)
- Title: `vX.Y.Z`
- Description: Copy from CHANGELOG.md
- Click "Publish release"

**Alternative: Command line**

```bash
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file CHANGELOG.md
```

### 4. Automated Steps (GitHub Actions)

When release is published, GitHub Actions automatically:
1. Runs full test suite
2. Builds package with version from git tag
3. Publishes to PyPI (via trusted publishing)
4. Uploads release artifacts
5. Triggers Homebrew formula update

### 5. Verify Release

**Check GitHub Actions:**
- Visit Actions tab
- Verify release workflow completed successfully

**Check PyPI:**
- Visit https://pypi.org/project/tui-delta/
- Verify new version appears

**Test installation:**
```bash
pip install tui-delta==X.Y.Z
tui-delta --version
```

---

## Branch Protection Setup

**REQUIRED: Main branch must be protected before first release.**

GitHub repository settings → Branches → Add branch protection rule for `main`:

**Required settings:**
- ✅ Require a pull request before merging
  - ✅ Require approvals (if team has multiple people)
- ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  - Add required checks: `quality`, `link-check`, `test (3.9)`, `test (3.10)`, etc.
- ✅ Do not allow bypassing the above settings
  - **CRITICAL:** Ensure "Allow administrators to bypass" is DISABLED
- ✅ Require conversation resolution before merging

---

## Versioning

**This project uses `hatch-vcs` - version comes from git tags, not files.**

No manual version updates needed in:
- `pyproject.toml` (has `dynamic = ["version"]`)
- `__init__.py` (imports from auto-generated `_version.py`)

**Semantic Versioning (SemVer):**
- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features (backward compatible)
- **PATCH** (0.0.X): Bug fixes (backward compatible)

---

## Hotfix Releases

**For critical bugs in production:**

1. Create hotfix branch from tag:
```bash
git checkout -b hotfix/vX.Y.Z+1 vX.Y.Z
```

2. Fix bug, commit, create PR (follow branch protection)

3. After PR merged, tag and release:
```bash
git checkout main
git pull
git tag -a vX.Y.Z+1 -m "Hotfix: description"
git push origin vX.Y.Z+1
```

4. Create GitHub release (same as normal release)

---

## Troubleshooting

### Release Workflow Failed

1. Check GitHub Actions logs to identify failure
2. Fix the issue
3. Delete failed tag:
```bash
git tag -d vX.Y.Z                    # Local
git push origin :refs/tags/vX.Y.Z   # Remote
```
4. Recreate and push tag after fix

### PyPI Upload Failed

**Common issues:**
- Version already exists (can't overwrite - increment version)
- Invalid credentials (check trusted publishing setup)
- Package validation failed (check build locally)

### Homebrew Update Failed

Check `update-homebrew` workflow logs. May need manual trigger:
1. Go to Actions → Update Homebrew Formula
2. Click "Run workflow"
3. Enter version number
4. Run

---

## Related Workflows

- [Feature Development](./feature-development.md) - Adding features
- [Bug Fixing](./bug-fixing.md) - Fixing bugs
- [CI/CD](./ci-cd.md) - Continuous integration setup
