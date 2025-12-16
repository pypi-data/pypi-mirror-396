"""Tests for __main__ module entry point."""

import subprocess
import sys

import pytest


@pytest.mark.integration
def test_main_module_list_profiles():
    """Test running tui-delta list-profiles as a module."""
    result = subprocess.run(
        [sys.executable, "-m", "tui_delta", "list-profiles"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "claude_code" in result.stdout or "claude_code" in result.stderr


@pytest.mark.integration
def test_main_module_help():
    """Test python -m tui-delta --help."""
    result = subprocess.run(
        [sys.executable, "-m", "tui_delta", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "run" in result.stdout.lower() or "list-profiles" in result.stdout.lower()


@pytest.mark.integration
def test_main_module_version():
    """Test python -m tui-delta --version."""
    result = subprocess.run(
        [sys.executable, "-m", "tui_delta", "--version"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "tui-delta version" in result.stdout


@pytest.mark.integration
def test_main_module_version_short():
    """Test python -m tui-delta -v."""
    result = subprocess.run(
        [sys.executable, "-m", "tui_delta", "-v"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "tui-delta version" in result.stdout
