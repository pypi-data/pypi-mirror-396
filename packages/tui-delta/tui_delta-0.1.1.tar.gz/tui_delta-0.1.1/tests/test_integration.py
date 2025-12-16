"""Integration tests for end-to-end Claude Code pipeline."""

import subprocess
import sys
from pathlib import Path

import pytest

from tui_delta.run import build_pipeline_commands

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
REAL_CLAUDE_SESSION = FIXTURES_DIR / "real-claude-session.bin"
REAL_CLAUDE_SESSION_EXPECTED = FIXTURES_DIR / "real-claude-session-expected-output.bin"


@pytest.mark.integration
class TestClaudeCodePipeline:
    """Integration tests with real Claude Code session data."""

    @pytest.fixture
    def mock_tui_command(self, tmp_path):
        """Create a mock TUI command that outputs the real Claude session data."""
        mock_script = tmp_path / "mock_claude.py"
        mock_script.write_text(f'''#!/usr/bin/env python3
import sys
fixture_path = r"{REAL_CLAUDE_SESSION}"
with open(fixture_path, "rb") as f:
    sys.stdout.buffer.write(f.read())
''')
        mock_script.chmod(0o755)
        return [sys.executable, str(mock_script)]

    def test_full_pipeline_with_run_function(self, mock_tui_command, tmp_path):
        """Test complete pipeline using run_tui_with_pipeline function.

        This tests the actual integration - the run.py module building and
        executing the pipeline, not manual subprocess wiring.
        """
        if not REAL_CLAUDE_SESSION.exists():
            pytest.skip(f"Real Claude Code session fixture not found: {REAL_CLAUDE_SESSION}")

        # Capture stdout by redirecting in subprocess
        test_script = tmp_path / "test_runner.py"
        test_script.write_text(f'''
import sys
sys.path.insert(0, r"{Path(__file__).parent.parent / "src"}")
from tui_delta.run import run_tui_with_pipeline

exit_code = run_tui_with_pipeline(
    command={mock_tui_command},
    profile="claude_code",
)
sys.exit(exit_code)
''')

        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True,
            timeout=60,
        )

        # Verify pipeline completed successfully
        assert result.returncode == 0, f"Pipeline failed: {result.stderr.decode()}"

        # Verify we got output
        output = result.stdout
        assert len(output) > 0, "Pipeline produced no output"

        # Verify output is reasonable (not just whitespace)
        lines = output.decode("utf-8", errors="replace").strip().split("\n")
        non_empty_lines = [line for line in lines if line.strip()]
        assert len(non_empty_lines) > 0, "Pipeline produced only empty lines"

        # Verify output is significantly smaller than input (compression from deduplication)
        input_size = REAL_CLAUDE_SESSION.stat().st_size
        assert len(output) < input_size, (
            f"Pipeline output ({len(output)}) should be smaller than input ({input_size})"
        )

    def test_pipeline_commands_structure(self):
        """Test that build_pipeline_commands returns the correct pipeline structure."""
        pipeline = build_pipeline_commands(profile="claude_code")

        # Should have 5 stages: clear_lines, consolidate, uniqseq, cut, final uniqseq
        assert len(pipeline) == 5, f"Expected 5 pipeline stages, got {len(pipeline)}"

        # Stage 1: clear_lines
        assert "clear_lines" in " ".join(pipeline[0])
        assert "--prefixes" in pipeline[0]
        assert "--profile" in pipeline[0]
        assert "claude_code" in pipeline[0]

        # Stage 2: consolidate_clears
        assert "consolidate_clears" in " ".join(pipeline[1])

        # Stage 3: first uniqseq
        assert "uniqseq" in " ".join(pipeline[2])
        assert "--track" in pipeline[2]

        # Stage 4: cut (Python one-liner)
        assert "print(line[3:], end='')" in " ".join(pipeline[3])

        # Stage 5: additional_pipeline from claude_code profile (final uniqseq)
        assert "uniqseq" in " ".join(pipeline[4])

    @pytest.mark.slow
    def test_pipeline_golden_output(self):
        """Test pipeline output matches golden file exactly.

        This is the primary correctness test - it verifies the complete pipeline
        produces exactly the expected output for a real Claude Code session.

        Tests the pipeline components directly (not through run_tui_with_pipeline
        which includes the `script` wrapper that may add extra control sequences).

        Note: This test processes 14MB of data and may take 30+ seconds.
        """
        if not REAL_CLAUDE_SESSION.exists():
            pytest.skip(f"Real Claude Code session fixture not found: {REAL_CLAUDE_SESSION}")
        if not REAL_CLAUDE_SESSION_EXPECTED.exists():
            pytest.skip(f"Golden output file not found: {REAL_CLAUDE_SESSION_EXPECTED}")

        # Read input
        input_data = REAL_CLAUDE_SESSION.read_bytes()

        # Build pipeline matching run.py's build_pipeline_commands for claude_code profile
        # Stage 1: clear_lines
        clear_lines_proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "tui_delta.clear_lines",
                "--prefixes",
                "--profile",
                "claude_code",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Stage 2: consolidate_clears
        consolidate_proc = subprocess.Popen(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            stdin=clear_lines_proc.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        clear_lines_proc.stdout.close()

        # Stage 3: first uniqseq
        uniqseq1_proc = subprocess.Popen(
            [sys.executable, "-m", "uniqseq", "--track", r"^\+: ", "--quiet"],
            stdin=consolidate_proc.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        consolidate_proc.stdout.close()

        # Stage 4: cut -b 4- (strip prefix)
        cut_proc = subprocess.Popen(
            [sys.executable, "-c", "import sys; [print(line[3:], end='') for line in sys.stdin]"],
            stdin=uniqseq1_proc.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        uniqseq1_proc.stdout.close()

        # Stage 5: final uniqseq
        uniqseq2_proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uniqseq",
                "--track",
                r"^\S",
                "--quiet",
                "--max-history",
                "5",
                "--window-size",
                "1",
                "--max-unique-sequences",
                "0",
            ],
            stdin=cut_proc.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        cut_proc.stdout.close()

        # Feed input and get output
        clear_lines_proc.stdin.write(input_data)
        clear_lines_proc.stdin.close()
        actual_output, _ = uniqseq2_proc.communicate(timeout=60)

        # Load expected output
        expected_output = REAL_CLAUDE_SESSION_EXPECTED.read_bytes()

        # Compare byte-for-byte
        if actual_output != expected_output:
            actual_lines = actual_output.decode("utf-8", errors="replace").splitlines()
            expected_lines = expected_output.decode("utf-8", errors="replace").splitlines()

            # Find first difference
            for i, (actual_line, expected_line) in enumerate(zip(actual_lines, expected_lines)):
                if actual_line != expected_line:
                    pytest.fail(
                        f"Output differs from golden file at line {i + 1}:\n"
                        f"Expected: {expected_line[:100]!r}\n"
                        f"Actual:   {actual_line[:100]!r}"
                    )

            # Different number of lines
            if len(actual_lines) != len(expected_lines):
                pytest.fail(
                    f"Output has {len(actual_lines)} lines, expected {len(expected_lines)} lines"
                )

            pytest.fail("Output differs from golden file")


@pytest.mark.integration
class TestGenericProfile:
    """Integration tests with generic profile."""

    def test_generic_profile_pipeline(self):
        """Test pipeline structure with generic profile."""
        pipeline = build_pipeline_commands(profile="generic")

        # Generic should have 4 stages (no additional_pipeline)
        # clear_lines, consolidate, uniqseq, cut
        assert len(pipeline) == 4, f"Expected 4 pipeline stages for generic, got {len(pipeline)}"


@pytest.mark.integration
class TestProfileSystem:
    """Integration tests for profile system."""

    def test_list_profiles_cli(self):
        """Test listing available profiles via CLI."""
        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.cli", "list-profiles"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # CLI uses rich console which outputs to stderr
        output = result.stdout + result.stderr
        assert "claude_code" in output
        assert "generic" in output
        assert "minimal" in output

    def test_profile_descriptions(self):
        """Verify profiles have descriptions."""
        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.cli", "list-profiles"],
            capture_output=True,
            text=True,
        )

        # Should show descriptions, not just names
        # CLI uses rich console which outputs to stderr
        output = result.stdout + result.stderr
        assert "Claude Code" in output or "terminal UI" in output
