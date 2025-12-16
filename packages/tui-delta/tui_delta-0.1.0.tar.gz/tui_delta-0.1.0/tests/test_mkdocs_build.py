"""Test that MkDocs documentation builds successfully."""

import os
import subprocess
import sys
from pathlib import Path


def test_mkdocs_build():
    """Test that mkdocs build completes without errors."""
    # Run from project root where mkdocs.yml is located
    project_root = Path(__file__).parent.parent

    # Add venv bin to PATH for mkdocs command
    env = os.environ.copy()
    venv_bin = Path(sys.executable).parent
    env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"

    result = subprocess.run(
        ["mkdocs", "build", "--strict"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=project_root,
        env=env,
    )

    assert result.returncode == 0, (
        f"mkdocs build failed with exit code {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
