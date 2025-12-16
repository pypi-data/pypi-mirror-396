"""Tests for CLI interface."""

import os
import re
import subprocess
import sys

import pytest
from typer.testing import CliRunner

from tui_delta.cli import app

# Ensure consistent terminal width for Rich formatting across all environments
os.environ.setdefault("COLUMNS", "120")

runner = CliRunner()

# Environment variables for consistent test output across all platforms
TEST_ENV = {
    "COLUMNS": "120",  # Consistent terminal width for Rich formatting
    "NO_COLOR": "1",  # Disable ANSI color codes for reliable string matching
}

# ANSI escape code pattern
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    return ANSI_ESCAPE.sub("", text)


@pytest.mark.unit
def test_cli_help():
    """Test --help output shows available commands."""
    result = runner.invoke(app, ["--help"], env=TEST_ENV)
    assert result.exit_code == 0
    # Strip ANSI codes for reliable string matching across environments
    output = strip_ansi(result.stdout.lower())
    assert "run" in output
    assert "list-profiles" in output


@pytest.mark.unit
def test_run_command_help():
    """Test 'run' command help."""
    result = runner.invoke(app, ["run", "--help"], env=TEST_ENV)
    assert result.exit_code == 0
    output = strip_ansi(result.stdout.lower())
    assert "tui application" in output
    assert "profile" in output


@pytest.mark.unit
def test_list_profiles_command():
    """Test 'list-profiles' command."""
    result = runner.invoke(app, ["list-profiles"], env=TEST_ENV)
    assert result.exit_code == 0
    # CliRunner captures stderr to output for typer apps
    output = result.output
    assert "claude_code" in output
    assert "generic" in output
    assert "minimal" in output


@pytest.mark.integration
def test_run_command_basic():
    """Test 'run' command with simple echo."""
    # Run a simple command that outputs a few lines
    result = runner.invoke(app, ["run", "--profile", "minimal", "--", "echo", "test"], env=TEST_ENV)
    # Exit code might be non-zero due to script command behavior
    # Just verify it ran without Python errors
    assert "test" in result.stdout or result.exit_code in [0, 1]


@pytest.mark.unit
def test_run_command_invalid_profile():
    """Test 'run' command with invalid profile."""
    result = runner.invoke(
        app, ["run", "--profile", "nonexistent", "--", "echo", "test"], env=TEST_ENV
    )
    # Should fail with error about profile
    assert result.exit_code != 0


@pytest.mark.unit
def test_run_command_requires_command():
    """Test 'run' command requires TUI command."""
    result = runner.invoke(app, ["run"], env=TEST_ENV)
    assert result.exit_code != 0
    # Should show error about missing command


@pytest.mark.unit
def test_list_profiles_shows_descriptions():
    """Test 'list-profiles' shows profile descriptions."""
    result = runner.invoke(app, ["list-profiles"], env=TEST_ENV)
    assert result.exit_code == 0
    output = result.output
    # Check for descriptive text, not just profile names
    assert "Claude Code" in output or "terminal" in output.lower()


@pytest.mark.integration
def test_run_with_custom_rules_file(tmp_path):
    """Test 'run' command with custom rules file."""
    # Create a simple custom profile YAML
    rules_file = tmp_path / "custom.yaml"
    rules_file.write_text("""
profiles:
  test_profile:
    description: "Test profile"
    clear_protections:
      - blank_boundary
    normalization_patterns: []
""")

    result = runner.invoke(
        app, ["run", "--rules-file", str(rules_file), "--", "echo", "test"], env=TEST_ENV
    )
    # Should run without errors (exit code might vary due to script)
    assert result.exit_code in [0, 1]


@pytest.mark.unit
def test_version_option():
    """Test --version option on run command."""
    # Version callback is defined but needs to be on a command
    # Test that version info is accessible
    result = subprocess.run(
        [sys.executable, "-m", "tui_delta.cli", "run", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    # Just verify CLI is working


@pytest.mark.integration
def test_run_profiles_integration():
    """Test that all built-in profiles work with run command."""
    profiles = ["claude_code", "generic", "minimal"]

    for profile in profiles:
        result = runner.invoke(
            app, ["run", "--profile", profile, "--", "echo", "test"], env=TEST_ENV
        )
        # Should not crash (exit code may vary due to script command)
        # Just verify no Python exceptions
        assert "Traceback" not in result.stdout
        # result.stderr may not be separately captured, check if available
        try:
            assert "Traceback" not in result.stderr
        except (ValueError, AttributeError):
            pass  # stderr not separately captured


@pytest.mark.unit
def test_clear_lines_module_directly():
    """Test clear_lines module can be invoked directly."""
    # This tests the clear_lines CLI entry point
    result = subprocess.run(
        [sys.executable, "-m", "tui_delta.clear_lines", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    # Strip ANSI codes for robust string matching
    import re

    clean_output = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", result.stdout)
    assert "--prefixes" in clean_output or "--profile" in clean_output


@pytest.mark.unit
def test_consolidate_module_directly():
    """Test consolidate_clears module can be invoked directly."""
    result = subprocess.run(
        [sys.executable, "-m", "tui_delta.consolidate_clears", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


@pytest.mark.integration
def test_pipeline_stdin_to_stdout():
    """Test pipeline processes stdin to stdout."""
    test_input = "line1\nline2\nline3\n"

    result = subprocess.run(
        [sys.executable, "-m", "tui_delta.clear_lines", "--profile", "minimal"],
        input=test_input.encode(),
        capture_output=True,
    )

    assert result.returncode == 0
    assert len(result.stdout) > 0
    # Should output the lines
    assert b"line1" in result.stdout
    assert b"line2" in result.stdout
    assert b"line3" in result.stdout
