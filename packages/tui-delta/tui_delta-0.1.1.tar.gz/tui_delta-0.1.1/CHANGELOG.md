# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

No unreleased changes yet.

---

## [0.1.1] - 2025-12-11

Updated description.

## [0.1.0] - 2025-12-11

Initial release.

### Features
- TUI application capture and delta processing
- Profile-based processing with built-in profile for Claude Code
- Clear detection and consolidation for terminal output
- Real-time streaming output
- Deduplication of repeated content blocks via uniqseq
- Multi-line pattern recognition via patterndb-yaml
- Command-line interface with typer and rich
- Comprehensive test suite with property-based testing
- Documentation site with MkDocs Material
- GitHub Actions CI/CD pipeline
- PyPI and Homebrew distribution support

---

## Release Process

Releases are automated via GitHub Actions when a version tag is pushed:

1. Update CHANGELOG.md with release notes
2. Create and push Git tag: `git tag v0.1.0 && git push origin v0.1.0`
3. GitHub Actions automatically:
   - Creates GitHub Release
   - Publishes to PyPI (when configured)
4. Version number is automatically derived from Git tag

[Unreleased]: https://github.com/JeffreyUrban/tui-delta/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/JeffreyUrban/tui-delta/releases/tag/v0.1.0
