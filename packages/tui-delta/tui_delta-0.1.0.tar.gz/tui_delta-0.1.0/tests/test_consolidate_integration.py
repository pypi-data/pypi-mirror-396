"""Integration tests for consolidate_clears main() state machine."""

import subprocess
import sys

import pytest


@pytest.mark.integration
class TestConsolidateStateMachine:
    """Test consolidate_clears state machine with various input patterns."""

    def test_kept_only_sequence(self):
        """Test with only kept lines."""
        test_input = "+: line1\n+: line2\n+: line3\n+: line4\n+: line5\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # All kept lines should pass through
        for i in range(1, 6):
            assert f"line{i}" in result.stdout

    def test_cleared_only_sequence(self):
        """Test with only cleared lines."""
        test_input = "\\: cleared1\n\\: cleared2\n\\: cleared3\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # First cleared block should be output
        assert "cleared" in result.stdout

    def test_kept_then_cleared(self):
        """Test transition from kept to cleared."""
        test_input = "+: kept1\n+: kept2\n\\: cleared1\n\\: cleared2\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "kept1" in result.stdout
        assert "kept2" in result.stdout

    def test_cleared_then_kept(self):
        """Test transition from cleared to kept."""
        test_input = "\\: cleared1\n\\: cleared2\n+: kept1\n+: kept2\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "kept1" in result.stdout
        assert "kept2" in result.stdout

    def test_alternating_kept_cleared(self):
        """Test alternating between kept and cleared."""
        test_input = "+: kept1\n\\: cleared1\n+: kept2\n\\: cleared2\n+: kept3\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Kept lines should all appear
        assert "kept1" in result.stdout
        assert "kept2" in result.stdout
        assert "kept3" in result.stdout

    def test_multiple_cleared_blocks_separated(self):
        """Test multiple cleared blocks with kept lines between."""
        test_input = "\\: block1_a\n\\: block1_b\n+: kept_separator\n\\: block2_a\n\\: block2_b\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "kept_separator" in result.stdout

    def test_command_lines_interspersed(self):
        """Test command lines (>:) mixed with other types."""
        test_input = (
            "+: kept1\n>: [window-title:test]\n\\: cleared1\n>: [window-title:test2]\n+: kept2\n"
        )

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "kept1" in result.stdout
        assert "kept2" in result.stdout

    def test_slash_prefix_cleared_lines(self):
        """Test cleared lines with forward slash prefix."""
        test_input = "/: cleared1\n/: cleared2\n/: cleared3\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "cleared" in result.stdout

    def test_mixed_backslash_slash_prefixes(self):
        """Test mixing backslash and forward slash cleared prefixes."""
        test_input = "\\: cleared1\n/: cleared2\n\\: cleared3\n/: cleared4\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert result.stdout != ""


@pytest.mark.integration
class TestConsolidateFileInput:
    """Test consolidate_clears with file input instead of stdin."""

    def test_file_input_basic(self, tmp_path):
        """Test reading from file instead of stdin."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("+: line1\n+: line2\n+: line3\n")

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears", str(input_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "line1" in result.stdout
        assert "line2" in result.stdout
        assert "line3" in result.stdout

    def test_file_input_with_cleared(self, tmp_path):
        """Test file input with cleared lines."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("\\: cleared1\n\\: cleared2\n+: kept1\n")

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears", str(input_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "kept1" in result.stdout

    def test_file_input_empty(self, tmp_path):
        """Test file input with empty file."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("")

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears", str(input_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert result.stdout == ""


@pytest.mark.integration
class TestConsolidateEdgeCases:
    """Test consolidate_clears edge cases and boundary conditions."""

    def test_single_kept_line(self):
        """Test with single kept line."""
        test_input = "+: only_line\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "only_line" in result.stdout

    def test_single_cleared_line(self):
        """Test with single cleared line."""
        test_input = "\\: only_cleared\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "only_cleared" in result.stdout

    def test_single_command_line(self):
        """Test with single command line."""
        test_input = ">: [window-title:test]\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Command lines are processed
        assert result.returncode == 0

    def test_very_long_lines(self):
        """Test with very long line content."""
        long_content = "x" * 10000
        test_input = f"+: {long_content}\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert long_content in result.stdout

    def test_special_characters_in_content(self):
        """Test with special characters in line content."""
        test_input = "+: line with\ttabs\n+: and: colons:\n+: [brackets]\n+: $pecial ch@rs!\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "tabs" in result.stdout
        assert "colons" in result.stdout
        assert "brackets" in result.stdout

    def test_unicode_content(self):
        """Test with unicode characters."""
        test_input = "+: Hello 世界\n+: Emoji 🎉🚀\n+: Ñoño\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "世界" in result.stdout or "Hello" in result.stdout

    def test_empty_line_content(self):
        """Test with empty line after prefix."""
        test_input = "+: \n+: \n+: content\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "content" in result.stdout

    def test_whitespace_only_content(self):
        """Test with whitespace-only content."""
        test_input = "+:    \n+:  spaces  \n+: \t\ttabs\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should handle whitespace content
        assert result.stdout != ""


@pytest.mark.integration
class TestConsolidateWithFlags:
    """Test consolidate_clears with various CLI flags."""

    def test_diff_flag_with_cleared_changes(self):
        """Test --diff flag shows changes between cleared blocks."""
        test_input = (
            "\\: old line 1\n\\: old line 2\n+: separator\n\\: new line 1\n\\: new line 2\n"
        )

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears", "--diff"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # With diff, should show both blocks
        assert result.stdout != ""

    def test_no_diff_flag_suppresses_diffs(self):
        """Test --no-diff flag suppresses diff output."""
        test_input = (
            "\\: block1 line1\n\\: block1 line2\n+: separator\n\\: block2 line1\n\\: block2 line2\n"
        )

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears", "--no-diff"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should still output, just without diffs
        assert "separator" in result.stdout

    def test_help_flag(self):
        """Test --help flag displays help."""
        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Usage:" in result.stdout or "usage:" in result.stdout.lower()
        assert "--diff" in result.stdout or "diff" in result.stdout.lower()
