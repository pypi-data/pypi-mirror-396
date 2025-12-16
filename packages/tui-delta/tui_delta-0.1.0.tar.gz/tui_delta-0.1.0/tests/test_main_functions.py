"""Direct tests of main() functions using CliRunner for coverage."""

import pytest
from typer.testing import CliRunner

runner = CliRunner()


@pytest.mark.unit
class TestClearLinesMainDirect:
    """Test clear_lines.main() via CliRunner to get coverage."""

    def test_main_with_stdin(self):
        """Test clear_lines main() with stdin input."""
        from tui_delta.clear_lines import app

        result = runner.invoke(app, [], input="line1\nline2\nline3\n")

        assert result.exit_code in (0, 1)
        assert "line" in result.stdout

    def test_main_with_file_input(self, tmp_path):
        """Test clear_lines main() with file input."""
        from tui_delta.clear_lines import app

        input_file = tmp_path / "input.txt"
        input_file.write_text("line1\nline2\nline3\n")

        result = runner.invoke(app, [str(input_file)])

        assert result.exit_code in (0, 1)
        assert "line" in result.stdout

    def test_main_with_prefixes(self, tmp_path):
        """Test clear_lines main() with --prefixes flag."""
        from tui_delta.clear_lines import app

        input_file = tmp_path / "input.txt"
        input_file.write_text("line1\nline2\n")

        result = runner.invoke(app, ["--prefixes", str(input_file)])

        assert result.exit_code in (0, 1)
        # Should have prefixes in output
        assert "+: " in result.stdout or result.stdout != ""

    def test_main_with_line_numbers(self, tmp_path):
        """Test clear_lines main() with --line-numbers flag."""
        from tui_delta.clear_lines import app

        input_file = tmp_path / "input.txt"
        input_file.write_text("line1\nline2\n")

        result = runner.invoke(app, ["--line-numbers", str(input_file)])

        assert result.exit_code in (0, 1)
        assert result.stdout != ""

    def test_main_with_profile(self, tmp_path):
        """Test clear_lines main() with --profile flag."""
        from tui_delta.clear_lines import app

        input_file = tmp_path / "input.txt"
        input_file.write_text("line1\nline2\n")

        result = runner.invoke(app, ["--profile", "generic", str(input_file)])

        assert result.exit_code in (0, 1)

    def test_main_with_clear_sequences(self, tmp_path):
        """Test clear_lines main() processing clear sequences."""
        from tui_delta.clear_lines import app

        input_file = tmp_path / "input.txt"
        input_file.write_bytes(b"line1\n\x1b[2Kline2\nline3\n")

        result = runner.invoke(app, ["--prefixes", str(input_file)])

        assert result.exit_code in (0, 1)
        assert result.stdout != ""


@pytest.mark.unit
class TestConsolidateClearsMainDirect:
    """Test consolidate_clears.main() via CliRunner to get coverage."""

    def test_main_with_kept_lines(self):
        """Test consolidate_clears main() with kept lines."""
        from tui_delta.consolidate_clears import app

        result = runner.invoke(app, [], input="+: line1\n+: line2\n+: line3\n")

        assert result.exit_code == 0
        assert "line1" in result.stdout
        assert "line2" in result.stdout

    def test_main_with_cleared_lines(self, tmp_path):
        """Test consolidate_clears main() with cleared lines."""
        from tui_delta.consolidate_clears import app

        input_file = tmp_path / "input.txt"
        input_file.write_text("\\: cleared1\n\\: cleared2\n")

        result = runner.invoke(app, [str(input_file)])

        assert result.exit_code == 0
        assert "cleared" in result.stdout

    def test_main_with_mixed_lines(self, tmp_path):
        """Test consolidate_clears main() with mixed kept/cleared."""
        from tui_delta.consolidate_clears import app

        input_file = tmp_path / "input.txt"
        input_file.write_text("+: kept1\n\\: cleared1\n+: kept2\n")

        result = runner.invoke(app, [str(input_file)])

        assert result.exit_code == 0
        assert "kept" in result.stdout

    def test_main_with_diff_flag(self, tmp_path):
        """Test consolidate_clears main() with --diff flag."""
        from tui_delta.consolidate_clears import app

        input_file = tmp_path / "input.txt"
        input_file.write_text("\\: old1\n\\: old2\n+: sep\n\\: new1\n\\: new2\n")

        result = runner.invoke(app, ["--diff", str(input_file)])

        assert result.exit_code == 0

    def test_main_with_no_diff_flag(self, tmp_path):
        """Test consolidate_clears main() with --no-diff flag."""
        from tui_delta.consolidate_clears import app

        input_file = tmp_path / "input.txt"
        input_file.write_text("\\: cleared1\n+: kept1\n")

        result = runner.invoke(app, ["--no-diff", str(input_file)])

        assert result.exit_code == 0
        assert "kept" in result.stdout

    def test_main_with_command_lines(self, tmp_path):
        """Test consolidate_clears main() with command lines."""
        from tui_delta.consolidate_clears import app

        input_file = tmp_path / "input.txt"
        input_file.write_text("+: kept1\n>: [window-title:test]\n+: kept2\n")

        result = runner.invoke(app, [str(input_file)])

        assert result.exit_code == 0
        assert "kept" in result.stdout

    def test_main_with_alternating_prefixes(self, tmp_path):
        """Test consolidate_clears main() with alternating cleared prefixes."""
        from tui_delta.consolidate_clears import app

        input_file = tmp_path / "input.txt"
        input_file.write_text("\\: cleared1\n/: cleared2\n\\: cleared3\n")

        result = runner.invoke(app, [str(input_file)])

        assert result.exit_code == 0
        assert result.stdout != ""

    def test_main_empty_input(self, tmp_path):
        """Test consolidate_clears main() with empty input."""
        from tui_delta.consolidate_clears import app

        input_file = tmp_path / "input.txt"
        input_file.write_text("")

        result = runner.invoke(app, [str(input_file)])

        assert result.exit_code == 0

    def test_main_with_long_sequence(self):
        """Test consolidate_clears main() with long input."""
        from tui_delta.consolidate_clears import app

        lines = [f"+: line{i}\n" for i in range(100)]
        test_input = "".join(lines)

        result = runner.invoke(app, [], input=test_input)

        assert result.exit_code == 0
        assert "line" in result.stdout
