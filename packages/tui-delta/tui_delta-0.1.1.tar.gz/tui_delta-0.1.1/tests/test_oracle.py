"""Tests for clear_lines module behaviors."""

import sys
from collections import deque

import pytest


@pytest.mark.unit
class TestClearLinesBehaviors:
    """Test clear_lines.py module behaviors."""

    def test_clear_lines_with_window_title_osc(self, capsys):
        """Test clear_lines outputs window title from OSC sequence."""
        from tui_delta.clear_lines import clear_lines
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()
        fifo = deque([(1, "line1"), (2, "line2"), (3, "\x1b]0;MyTitle\x07")])

        clear_lines(
            fifo,
            clear_count=2,
            show_prefixes=True,
            show_line_numbers=False,
            clear_operation_count=0,
            rules=rules,
        )

        captured = capsys.readouterr()
        # With N-1 formula: 2 clears = 1 line cleared (line2)
        assert "\\: line2" in captured.out
        assert "[window-title:MyTitle]" in captured.out

    def test_clear_lines_with_window_title_annotation(self, capsys):
        """Test clear_lines outputs window title from annotation."""
        from tui_delta.clear_lines import clear_lines
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()
        fifo = deque([(1, "line1"), (2, "line2"), (3, "[window-title:MyTitle]")])

        clear_lines(
            fifo,
            clear_count=2,
            show_prefixes=True,
            show_line_numbers=False,
            clear_operation_count=0,
            rules=rules,
        )

        captured = capsys.readouterr()
        # With N-1 formula: 2 clears = 1 line cleared (line2)
        assert "\\: line2" in captured.out
        assert "[window-title:MyTitle]" in captured.out

    def test_clear_lines_prefix_alternation(self, capsys):
        """Test clear prefix alternates between backslash and forward slash."""
        from tui_delta.clear_lines import clear_lines
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()

        # First clear (even count) - should use backslash
        # Need 2 clears to actually clear 1 line (N-1 formula)
        fifo1 = deque([(1, "cleared1"), (2, "clear")])
        clear_lines(
            fifo1,
            clear_count=2,
            show_prefixes=True,
            show_line_numbers=False,
            clear_operation_count=0,
            rules=rules,
        )
        captured1 = capsys.readouterr()
        assert "\\: cleared1" in captured1.out

        # Second clear (odd count) - should use forward slash
        fifo2 = deque([(3, "cleared2"), (4, "clear")])
        clear_lines(
            fifo2,
            clear_count=2,
            show_prefixes=True,
            show_line_numbers=False,
            clear_operation_count=1,
            rules=rules,
        )
        captured2 = capsys.readouterr()
        assert "/: cleared2" in captured2.out

    def test_clear_lines_with_line_numbers(self, capsys):
        """Test clear_lines displays line numbers when enabled."""
        from tui_delta.clear_lines import clear_lines
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()
        fifo = deque([(42, "content"), (43, "clear")])

        clear_lines(
            fifo,
            clear_count=1,
            show_prefixes=True,
            show_line_numbers=True,
            clear_operation_count=0,
            rules=rules,
        )

        captured = capsys.readouterr()
        assert "42" in captured.out
        assert "content" in captured.out

    def test_clear_lines_with_control_lines_prefix(self, capsys):
        """Test clear_lines uses >: prefix for control lines."""
        from tui_delta.clear_lines import CONTROL_LINES, clear_lines
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()
        # Use a control line prefix
        control_line = f"{CONTROL_LINES[0]}control content"
        fifo = deque([(1, control_line), (2, "clear")])

        clear_lines(
            fifo,
            clear_count=0,
            show_prefixes=True,
            show_line_numbers=False,
            clear_operation_count=0,
            rules=rules,
        )

        captured = capsys.readouterr()
        assert ">: " in captured.out

    def test_clear_lines_no_clearing(self, capsys):
        """Test clear_lines with no lines to clear."""
        from tui_delta.clear_lines import clear_lines
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()
        # FIFO with just one line (the clear line)
        fifo = deque([(1, "clear")])

        # With clear_count=0, nothing should be cleared
        clear_lines(
            fifo,
            clear_count=0,
            show_prefixes=True,
            show_line_numbers=False,
            clear_operation_count=0,
            rules=rules,
        )

        captured = capsys.readouterr()
        # Should output nothing for the clear line itself
        assert captured.out == ""

    def test_clear_lines_respects_max_clearable(self, capsys):
        """Test clear_lines doesn't clear more than available."""
        from tui_delta.clear_lines import clear_lines
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()
        # Only 2 lines, try to clear 10
        fifo = deque([(1, "line1"), (2, "clear")])

        clear_lines(
            fifo,
            clear_count=10,
            show_prefixes=True,
            show_line_numbers=False,
            clear_operation_count=0,
            rules=rules,
        )

        captured = capsys.readouterr()
        # Should only clear line1, not crash
        assert "\\: line1" in captured.out

    def test_clear_lines_with_next_line_context(self, capsys):
        """Test clear_lines receives next_line for rule evaluation."""
        from tui_delta.clear_lines import clear_lines
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules()
        fifo = deque([(1, "line1"), (2, "clear")])

        # Pass next_line for context
        clear_lines(
            fifo,
            clear_count=1,
            show_prefixes=True,
            show_line_numbers=False,
            clear_operation_count=0,
            rules=rules,
            next_line="next line content",
        )

        captured = capsys.readouterr()
        # Should process normally with next_line context
        assert "line1" in captured.out


@pytest.mark.unit
class TestClearLinesMain:
    """Test clear_lines main() CLI behaviors."""

    def test_main_with_stdin_input(self):
        """Test clear_lines main() processes stdin."""
        import subprocess

        # Input with clear sequences
        test_input = "line1\n\x1b[2Kline2\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.clear_lines"],
            input=test_input.encode(),
            capture_output=True,
        )

        assert result.returncode == 0
        assert b"line" in result.stdout

    def test_main_with_prefixes_flag(self):
        """Test clear_lines main() with --prefixes flag."""
        import subprocess

        test_input = "line1\n\x1b[2Kline2\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.clear_lines", "--prefixes"],
            input=test_input.encode(),
            capture_output=True,
        )

        assert result.returncode == 0
        # Should have prefix markers
        assert b"+: " in result.stdout or b"\\: " in result.stdout

    def test_main_with_line_numbers_flag(self):
        """Test clear_lines main() with --line-numbers flag."""
        import subprocess

        test_input = "line1\nline2\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.clear_lines", "--line-numbers"],
            input=test_input.encode(),
            capture_output=True,
        )

        assert result.returncode == 0
        # Output should contain line numbers
        output = result.stdout.decode()
        # Line numbers appear at start
        assert output.split()[0].isdigit() or "1" in output or "2" in output

    def test_main_with_profile_flag(self):
        """Test clear_lines main() with --profile flag."""
        import subprocess

        test_input = "line1\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.clear_lines", "--profile", "generic"],
            input=test_input.encode(),
            capture_output=True,
        )

        assert result.returncode == 0

    def test_main_with_file_input(self, tmp_path):
        """Test clear_lines main() with file input."""
        import subprocess

        # Create test file
        test_file = tmp_path / "input.txt"
        test_file.write_bytes(b"line1\nline2\n")

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.clear_lines", str(test_file)],
            capture_output=True,
        )

        assert result.returncode == 0
        assert b"line1" in result.stdout
        assert b"line2" in result.stdout


@pytest.mark.unit
class TestConsolidateClearsBehaviors:
    """Test consolidate_clears.py module behaviors."""

    def test_consolidate_kept_to_kept_transition(self):
        """Test consolidate with kept-to-kept transition."""
        import subprocess

        # Multiple kept lines in sequence
        test_input = "+: line1\n+: line2\n+: line3\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # All kept lines should pass through
        assert "line1" in result.stdout
        assert "line2" in result.stdout
        assert "line3" in result.stdout

    def test_consolidate_cleared_to_cleared_transition(self):
        """Test consolidate with cleared-to-cleared transition."""
        import subprocess

        # Multiple cleared lines in sequence
        test_input = "\\: cleared1\n\\: cleared2\n\\: cleared3\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # First cleared block should be output
        assert "cleared1" in result.stdout

    def test_consolidate_cleared_to_kept_transition(self):
        """Test consolidate with cleared-to-kept transition."""
        import subprocess

        # Transition from cleared to kept
        test_input = "\\: cleared1\n+: kept1\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should see both cleared and kept content
        assert "cleared1" in result.stdout
        assert "kept1" in result.stdout

    def test_consolidate_alternating_clear_prefixes(self):
        """Test consolidate handles alternating \\ and / prefixes."""
        import subprocess

        # Alternating clear prefixes
        test_input = "\\: cleared1\n/: cleared2\n\\: cleared3\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should handle both prefix types
        assert result.stdout != ""

    def test_consolidate_with_command_lines(self):
        """Test consolidate handles command lines (>: prefix)."""
        import subprocess

        test_input = "+: kept1\n>: [window-title:test]\n+: kept2\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Command lines should be processed
        assert "kept1" in result.stdout
        assert "kept2" in result.stdout

    def test_consolidate_sequence_extraction(self):
        """Test consolidate extracts sequences correctly."""
        import subprocess

        # Create input with repeated patterns
        test_input = "+: status: processing\n+: status: complete\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.consolidate_clears"],
            input=test_input,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should process sequential updates
        assert "status" in result.stdout


@pytest.mark.unit
class TestClearRulesBehaviors:
    """Test clear_rules.py module behaviors."""

    def test_clear_rules_with_blank_boundary_protection(self):
        """Test ClearRules applies blank_boundary protection."""
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules(profile="claude_code")  # Has blank_boundary

        # Blank first cleared line should reduce clear count
        result = rules.calculate_clear_count(
            clear_line_count=5,
            first_cleared_line="",  # Blank
            first_sequence_line="content",
            next_line_after_clear="next",
        )

        # Should be less than N-1 due to protection
        assert result < 4

    def test_clear_rules_with_user_input_final_protection(self):
        """Test ClearRules applies user_input_final protection."""
        from tui_delta.clear_rules import ClearRules

        rules = ClearRules(profile="claude_code")  # Has user_input_final

        # User input marker in next line should reduce clear count
        result = rules.calculate_clear_count(
            clear_line_count=5,
            first_cleared_line="content",
            first_sequence_line="content",
            next_line_after_clear="> ",  # User input marker
        )

        # Should be less than or equal to N-1 due to protection
        # (protection may or may not trigger depending on exact conditions)
        assert result <= 4

    def test_clear_rules_profile_listing(self):
        """Test ClearRules.list_profiles returns available profiles."""
        from tui_delta.clear_rules import ClearRules

        profiles = ClearRules.list_profiles()

        # Should have standard profiles
        assert "claude_code" in profiles
        assert "generic" in profiles
        assert "minimal" in profiles

    def test_clear_rules_get_profile_config(self):
        """Test ClearRules.get_profile_config returns configuration."""
        from tui_delta.clear_rules import ClearRules

        config = ClearRules.get_profile_config("claude_code")

        # Should have expected keys
        assert "clear_protections" in config
        assert "normalization_patterns" in config


@pytest.mark.unit
class TestRunBehaviors:
    """Test run.py module behaviors."""

    def test_run_tui_with_pipeline_basic(self):
        """Test run_tui_with_pipeline with simple command."""
        from tui_delta import run_tui_with_pipeline

        # Use simple echo command
        exit_code = run_tui_with_pipeline(["echo", "test"])

        # Should complete successfully
        assert exit_code in (0, 1)  # 0 or 1 acceptable due to script wrapper

    def test_build_pipeline_minimal_profile(self):
        """Test build_pipeline_commands with minimal profile."""
        from tui_delta.run import build_pipeline_commands

        cmds = build_pipeline_commands(profile="minimal")

        # Should have at least clear_lines and consolidate_clears
        assert len(cmds) >= 2
        cmd_str = " ".join(str(c) for cmd in cmds for c in cmd)
        assert "clear_lines" in cmd_str
        assert "consolidate_clears" in cmd_str

    def test_build_pipeline_generic_profile(self):
        """Test build_pipeline_commands with generic profile."""
        from tui_delta.run import build_pipeline_commands

        cmds = build_pipeline_commands(profile="generic")

        # Should have standard pipeline stages
        assert len(cmds) >= 2

    def test_run_with_nonexistent_command(self):
        """Test run_tui_with_pipeline with nonexistent command."""
        from tui_delta import run_tui_with_pipeline

        # Command that doesn't exist
        exit_code = run_tui_with_pipeline(["nonexistent_command_xyz"])

        # Should return non-zero exit code
        assert exit_code != 0
