"""Tests specifically targeting coverage gaps to reach 95%+ coverage."""

import pytest
from rich.text import Text


@pytest.mark.unit
class TestConsolidateClearsCoverage:
    """Tests for uncovered consolidate_clears.py functions."""

    def test_char_diff_equal_lines(self):
        """Test _char_diff with identical lines."""
        from tui_delta.consolidate_clears import _char_diff

        result = _char_diff("hello", "hello")
        assert isinstance(result, Text)
        assert str(result) == "hello"

    def test_char_diff_pure_insert(self):
        """Test _char_diff with pure insertion."""
        from tui_delta.consolidate_clears import _char_diff

        result = _char_diff("hello", "hello world")
        assert isinstance(result, Text)
        # Should have " world" in green
        assert "hello world" in str(result)

    def test_char_diff_pure_delete(self):
        """Test _char_diff with pure deletion."""
        from tui_delta.consolidate_clears import _char_diff

        result = _char_diff("hello world", "hello")
        assert isinstance(result, Text)
        # Should have "hello" and red deletion marker
        assert "hello" in str(result)

    def test_char_diff_replacement(self):
        """Test _char_diff with replacement."""
        from tui_delta.consolidate_clears import _char_diff

        result = _char_diff("hello", "hallo")
        assert isinstance(result, Text)
        # Should have "h" + "a" (yellow) + "llo"
        assert "hallo" in str(result)

    def test_char_diff_delete_insert_pair(self):
        """Test _char_diff with delete+insert pair (treated as replacement)."""
        from tui_delta.consolidate_clears import _char_diff

        # This tests the delete+insert handling logic
        result = _char_diff("old", "new")
        assert isinstance(result, Text)
        assert "new" in str(result)

    def test_render_component_sequence_text_only(self):
        """Test _render_component_sequence with text components."""
        from tui_delta.consolidate_clears import _render_component_sequence

        components = [{"text": "hello"}, {"text": " "}, {"text": "world"}]
        result = _render_component_sequence(components)
        assert result == "hello world"

    def test_render_component_sequence_serialized(self):
        """Test _render_component_sequence with serialized components."""
        from tui_delta.consolidate_clears import _render_component_sequence

        components = [{"serialized": "[1-9]"}, {"text": " "}, {"serialized": "[a-z]+"}]
        result = _render_component_sequence(components)
        assert "[1-9] [a-z]+" in result

    def test_render_component_sequence_mixed(self):
        """Test _render_component_sequence with mixed components."""
        from tui_delta.consolidate_clears import _render_component_sequence

        components = [
            {"text": "prefix"},
            {"serialized": "\\d+"},
            {"text": "suffix"},
        ]
        result = _render_component_sequence(components)
        assert "prefix" in result
        assert "suffix" in result

    def test_render_component_sequence_empty(self):
        """Test _render_component_sequence with empty components."""
        from tui_delta.consolidate_clears import _render_component_sequence

        result = _render_component_sequence([])
        assert result == ""

    def test_normalize_with_none_engine(self):
        """Test normalize() with None engine."""
        from tui_delta.consolidate_clears import normalize

        lines = ["line1", "line2", "line3"]
        result = normalize(None, lines)
        # With None engine, should return lines unchanged
        assert result == lines

    def test_print_prefixed_line_with_console(self):
        """Test _print_prefixed_line with Rich console."""
        import io

        from rich.console import Console

        from tui_delta.consolidate_clears import _print_prefixed_line

        # Create console with string buffer
        buffer = io.StringIO()
        console = Console(file=buffer, force_terminal=True, width=80)

        _print_prefixed_line("+: ", "hello world", console)

        output = buffer.getvalue()
        assert "hello world" in output

    def test_print_prefixed_line_with_text_object(self):
        """Test _print_prefixed_line with Rich Text object."""
        import io

        from rich.console import Console
        from rich.text import Text

        from tui_delta.consolidate_clears import _print_prefixed_line

        buffer = io.StringIO()
        console = Console(file=buffer, force_terminal=True, width=80)

        text = Text("formatted", style="bold")
        _print_prefixed_line("+: ", text, console)

        output = buffer.getvalue()
        assert "formatted" in output

    def test_print_prefixed_line_without_console(self, capsys):
        """Test _print_prefixed_line without console (stdout)."""
        from tui_delta.consolidate_clears import _print_prefixed_line

        _print_prefixed_line("+: ", "hello", None)

        captured = capsys.readouterr()
        assert "+: hello" in captured.out

    def test_print_prefixed_line_with_style(self):
        """Test _print_prefixed_line with custom style."""
        import io

        from rich.console import Console

        from tui_delta.consolidate_clears import _print_prefixed_line

        buffer = io.StringIO()
        console = Console(file=buffer, force_terminal=True, width=80)

        _print_prefixed_line("+: ", "styled text", console, style="bold red")

        output = buffer.getvalue()
        assert "styled text" in output


@pytest.mark.unit
class TestClearLinesCoverage:
    """Tests for uncovered clear_lines.py functions."""

    def test_extract_osc_window_title_valid(self):
        """Test extract_osc_window_title with valid OSC sequence."""
        from tui_delta.clear_lines import extract_osc_window_title

        line = "\x1b]0;My Title\x07"
        result = extract_osc_window_title(line)
        assert result == "My Title"

    def test_extract_osc_window_title_code_2(self):
        """Test extract_osc_window_title with OSC code 2."""
        from tui_delta.clear_lines import extract_osc_window_title

        line = "\x1b]2;Window Title\x07"
        result = extract_osc_window_title(line)
        assert result == "Window Title"

    def test_extract_osc_window_title_invalid(self):
        """Test extract_osc_window_title with non-OSC line."""
        from tui_delta.clear_lines import extract_osc_window_title

        line = "regular text"
        result = extract_osc_window_title(line)
        assert result is None

    def test_extract_osc_window_title_empty(self):
        """Test extract_osc_window_title with empty string."""
        from tui_delta.clear_lines import extract_osc_window_title

        result = extract_osc_window_title("")
        assert result is None

    def test_count_clear_sequences_none(self):
        """Test count_clear_sequences with no clear sequences."""
        from tui_delta.clear_lines import count_clear_sequences

        line = "normal text without clears"
        result = count_clear_sequences(line)
        assert result == 0

    def test_count_clear_sequences_single(self):
        """Test count_clear_sequences with one clear sequence."""
        from tui_delta.clear_lines import count_clear_sequences

        line = "text\x1b[2Kmore text"
        result = count_clear_sequences(line)
        assert result == 1

    def test_count_clear_sequences_multiple(self):
        """Test count_clear_sequences with multiple clear sequences."""
        from tui_delta.clear_lines import count_clear_sequences

        line = "\x1b[2K\x1b[2K\x1b[2K"
        result = count_clear_sequences(line)
        assert result == 3


@pytest.mark.unit
class TestClearRulesCoverage:
    """Tests for uncovered clear_rules.py functions."""

    def test_calculate_clear_count_basic(self):
        """Test calculate_clear_count with basic N-1 formula."""
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()
        # With 5 clear sequences, should clear 4 lines
        result = rules.calculate_clear_count(5, "line1", "line2", "line3")
        assert result == 4

    def test_calculate_clear_count_zero(self):
        """Test calculate_clear_count with zero clears."""
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()
        result = rules.calculate_clear_count(0, "line1", "line2", "line3")
        assert result == 0

    def test_calculate_clear_count_one(self):
        """Test calculate_clear_count with one clear."""
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()
        # N-1 formula: 1 clear = 0 lines cleared
        result = rules.calculate_clear_count(1, "line1", "line2", "line3")
        assert result == 0


@pytest.mark.unit
class TestRunCoverage:
    """Tests for uncovered run.py functions."""

    def test_build_script_command_darwin(self):
        """Test build_script_command for macOS."""
        from tui_delta.run import build_script_command

        cmd = build_script_command(["echo", "test"], system="Darwin")
        assert "script" in cmd
        assert "-q" in cmd
        assert "-F" in cmd
        assert "/dev/stdout" in cmd
        assert "echo" in cmd
        assert "test" in cmd

    def test_build_script_command_linux(self):
        """Test build_script_command for Linux."""
        from tui_delta.run import build_script_command

        cmd = build_script_command(["ls", "-la"], system="Linux")
        assert "script" in cmd
        assert "--flush" in cmd
        assert "--quiet" in cmd
        assert "--return" in cmd
        assert "--command" in cmd
        assert "/dev/stdout" in cmd
        # Command is joined with shlex.join, so check the joined string
        assert "ls -la" in " ".join(cmd)

    def test_build_pipeline_commands_basic(self):
        """Test build_pipeline_commands with default profile."""
        from tui_delta.run import build_pipeline_commands

        cmds = build_pipeline_commands()
        # Should have clear_lines, consolidate_clears, uniqseq, cut, additional
        assert len(cmds) >= 4
        assert any("clear_lines" in str(cmd) for cmd in cmds)
        assert any("consolidate_clears" in str(cmd) for cmd in cmds)

    def test_build_pipeline_commands_with_profile(self):
        """Test build_pipeline_commands with specific profile."""
        from tui_delta.run import build_pipeline_commands

        cmds = build_pipeline_commands(profile="claude_code")
        assert any("clear_lines" in str(cmd) and "--profile" in str(cmd) for cmd in cmds)

    def test_build_pipeline_commands_with_rules_file(self):
        """Test build_pipeline_commands with custom rules file."""
        from pathlib import Path

        from tui_delta.run import build_pipeline_commands

        rules_path = Path("/tmp/custom_rules.yaml")
        cmds = build_pipeline_commands(rules_file=rules_path)
        assert any("--rules-file" in str(cmd) for cmd in cmds)


@pytest.mark.unit
class TestConsolidateClearsAdvanced:
    """Advanced integration tests for consolidate_clears.py."""

    def test_consolidate_with_no_diff_flag(self):
        """Test consolidate with --no-diff flag."""
        import subprocess
        import sys

        test_input = "\\: line1\n\\: line2\n\\: line3\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears", "--no-diff"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert result.stdout != ""

    def test_consolidate_with_multiple_cleared_blocks(self):
        """Test consolidate with multiple distinct cleared blocks."""
        import subprocess
        import sys

        # Two separate cleared blocks separated by kept line
        test_input = (
            "\\: block1_line1\n\\: block1_line2\n+: kept\n\\: block2_line1\n\\: block2_line2\n"
        )

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should process both blocks
        assert "block1" in result.stdout or "block2" in result.stdout

    def test_consolidate_long_sequence(self):
        """Test consolidate with long sequence of lines."""
        import subprocess
        import sys

        # Generate long sequence
        lines = [f"+: line{i}\n" for i in range(100)]
        test_input = "".join(lines)

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should handle long sequences
        assert "line" in result.stdout


@pytest.mark.unit
class TestClearLinesAdvanced:
    """Advanced tests for clear_lines.py edge cases."""

    def test_format_line_with_prefix_and_line_number(self):
        """Test _format_line with both prefix and line number."""
        from tui_delta.clear_lines import _format_line

        result = _format_line("+: ", 42, "test content", show_prefixes=True, show_line_numbers=True)

        assert "42" in result
        assert "+: " in result
        assert "test content" in result

    def test_format_line_without_line_number(self):
        """Test _format_line without line number."""
        from tui_delta.clear_lines import _format_line

        result = _format_line(
            "+: ", 42, "test content", show_prefixes=True, show_line_numbers=False
        )

        assert "42" not in result
        assert "+: " in result
        assert "test content" in result

    def test_format_line_empty_content(self):
        """Test _format_line with empty content."""
        from tui_delta.clear_lines import _format_line

        result = _format_line("+: ", 1, "", show_prefixes=True, show_line_numbers=False)

        assert "+: " in result

    def test_clear_lines_with_window_title_icon_annotation(self, capsys):
        """Test clear_lines with window-title-icon annotation."""
        from collections import deque

        from tui_delta.clear_lines import clear_lines
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()
        fifo = deque([(1, "line1"), (2, "[window-title-icon:MyIcon]")])

        clear_lines(
            fifo,
            clear_count=0,
            show_prefixes=True,
            show_line_numbers=False,
            clear_operation_count=0,
            rules=rules,
        )

        captured = capsys.readouterr()
        # Should extract and output window title icon
        assert "[window-title-icon:MyIcon]" in captured.out

    def test_clear_lines_multiple_clears(self, capsys):
        """Test clear_lines with multiple lines to clear."""
        from collections import deque

        from tui_delta.clear_lines import clear_lines
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()
        # 5 lines in FIFO
        fifo = deque([(1, "line1"), (2, "line2"), (3, "line3"), (4, "line4"), (5, "clear")])

        # Clear 3 lines (with N-1 formula: 4 clears = 3 lines cleared)
        clear_lines(
            fifo,
            clear_count=4,
            show_prefixes=True,
            show_line_numbers=False,
            clear_operation_count=0,
            rules=rules,
        )

        captured = capsys.readouterr()
        # Should have cleared line2, line3, line4 and kept line1
        assert "+: line1" in captured.out
        assert "\\: line2" in captured.out
        assert "\\: line3" in captured.out
        assert "\\: line4" in captured.out


@pytest.mark.unit
class TestClearRulesAdvanced:
    """Advanced tests for clear_rules.py edge cases."""

    def test_calculate_clear_count_with_none_lines(self):
        """Test calculate_clear_count with None line parameters."""
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()

        result = rules.calculate_clear_count(
            clear_line_count=3,
            first_cleared_line=None,
            first_sequence_line=None,
            next_line_after_clear=None,
        )

        # Should still apply N-1 formula
        assert result == 2

    def test_calculate_clear_count_large_number(self):
        """Test calculate_clear_count with large clear count."""
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()

        result = rules.calculate_clear_count(
            clear_line_count=1000,
            first_cleared_line="content",
            first_sequence_line="content",
            next_line_after_clear="next",
        )

        # Should apply N-1 formula
        assert result == 999

    def test_get_profile_config_minimal(self):
        """Test get_profile_config for minimal profile."""
        from tui_delta.clear_rules import ClearRules

        config = ClearRules.get_profile_config("minimal")

        assert "clear_protections" in config
        assert isinstance(config["clear_protections"], list)

    def test_get_profile_config_generic(self):
        """Test get_profile_config for generic profile."""
        from tui_delta.clear_rules import ClearRules

        config = ClearRules.get_profile_config("generic")

        assert "clear_protections" in config
        assert "normalization_patterns" in config


@pytest.mark.unit
class TestMainModuleCoverage:
    """Tests for __main__.py coverage."""

    def test_main_module_imports(self):
        """Test that __main__ module imports correctly."""
        import tui_delta.__main__

        # Module should import without errors
        assert hasattr(tui_delta.__main__, "app")


@pytest.mark.unit
class TestConsolidateClearsMainCLI:
    """Integration tests for consolidate_clears main() CLI."""

    def test_main_with_kept_lines(self, tmp_path):
        """Test consolidate_clears main() with kept lines."""
        import subprocess
        import sys

        # Create test input with kept lines only
        test_input = "+: line1\n+: line2\n+: line3\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "+: line1" in result.stdout
        assert "+: line2" in result.stdout
        assert "+: line3" in result.stdout

    def test_main_with_cleared_lines(self, tmp_path):
        """Test consolidate_clears main() with cleared lines."""
        import subprocess
        import sys

        # Create test input with cleared lines
        test_input = "\\: line1\n\\: line2\n\\: line3\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # First cleared block should be output in full
        assert "line1" in result.stdout

    def test_main_with_mixed_lines(self, tmp_path):
        """Test consolidate_clears main() with mixed line types."""
        import subprocess
        import sys

        # Create test input with mixed types
        test_input = "+: kept1\n\\: cleared1\n+: kept2\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "kept1" in result.stdout
        assert "kept2" in result.stdout

    def test_main_with_empty_input(self, tmp_path):
        """Test consolidate_clears main() with empty input."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input="",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert result.stdout == ""

    def test_main_with_diff_flag(self, tmp_path):
        """Test consolidate_clears main() with --diff flag."""
        import subprocess
        import sys

        test_input = "\\: line1\n\\: line2\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears", "--diff"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_extract_sequence_block_no_sequences(self):
        """Test _extract_sequence_block with no sequence configs."""
        from tui_delta.consolidate_clears import _extract_sequence_block

        lines = ["line1", "line2", "line3"]
        normalized = ["line1", "line2", "line3"]

        non_seq, seq, non_seq_norm, seq_norm = _extract_sequence_block(
            lines, normalized, None, None
        )

        # With no configs, should return all as non-sequence
        assert non_seq == lines
        assert seq == []
        assert non_seq_norm == normalized
        assert seq_norm == []

    def test_extract_sequence_block_empty_configs(self):
        """Test _extract_sequence_block with empty configs."""
        from tui_delta.consolidate_clears import _extract_sequence_block

        lines = ["line1", "line2"]
        normalized = ["line1", "line2"]

        non_seq, seq, non_seq_norm, seq_norm = _extract_sequence_block(lines, normalized, {}, set())

        # With empty configs, should return all as non-sequence
        assert non_seq == lines
        assert seq == []


@pytest.mark.unit
class TestInitModuleCoverage:
    """Tests for __init__.py coverage."""

    def test_version_export(self):
        """Test that __version__ is exported."""
        import tui_delta

        assert hasattr(tui_delta, "__version__")
        assert isinstance(tui_delta.__version__, str)

    def test_clear_rules_export(self):
        """Test that ClearRules is exported."""
        import tui_delta

        assert hasattr(tui_delta, "ClearRules")
        # Should be able to instantiate it
        rules = tui_delta.ClearRules()
        assert rules is not None

    def test_run_tui_with_pipeline_export(self):
        """Test that run_tui_with_pipeline is exported."""
        import tui_delta

        assert hasattr(tui_delta, "run_tui_with_pipeline")
        # Should be a callable
        assert callable(tui_delta.run_tui_with_pipeline)
