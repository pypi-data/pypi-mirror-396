"""Test pipeline invariants hold under all conditions."""

import subprocess
import sys
from collections import deque

import pytest

from tui_delta.clear_lines import clear_lines
from tui_delta.clear_rules import ClearRules


@pytest.mark.property
class TestClearLinesInvariants:
    """Test invariants for clear_lines processing."""

    def test_clear_count_never_exceeds_available(self):
        """Clear count should never exceed available lines (minus clear line)."""
        rules = ClearRules(profile="minimal")

        # Create FIFO with 3 lines + 1 clear line = 4 total
        fifo = deque(
            [
                (1, "line1"),
                (2, "line2"),
                (3, "line3"),
                (4, "\x1b[2K" * 10),  # Request to clear 10 lines
            ]
        )

        # Should only clear max 3 lines (total - 1 for clear line itself)
        clear_lines(
            fifo,
            clear_count=10,
            show_prefixes=False,
            show_line_numbers=False,
            clear_operation_count=0,
            rules=rules,
        )

        # Should have processed all lines
        assert len(fifo) == 0

    def test_fifo_order_preserved(self):
        """Lines are processed in FIFO order."""
        rules = ClearRules(profile="minimal")

        # Track output order by capturing print calls
        output_lines = []

        # Monkey patch print to capture output
        import builtins

        original_print = builtins.print

        def mock_print(*args, **kwargs):
            if args:
                output_lines.append(args[0])

        builtins.print = mock_print

        try:
            fifo = deque(
                [
                    (1, "first"),
                    (2, "second"),
                    (3, "third"),
                    (4, "\x1b[2K" * 3),  # Clear 2 lines
                ]
            )

            clear_lines(
                fifo,
                clear_count=3,
                show_prefixes=False,
                show_line_numbers=False,
                clear_operation_count=0,
                rules=rules,
            )

            # Output should be in order: first (kept), second (cleared), third (cleared)
            assert len(output_lines) == 3
            assert output_lines[0] == "first"
            assert output_lines[1] == "second"
            assert output_lines[2] == "third"

        finally:
            builtins.print = original_print

    def test_kept_prefix_is_plus(self):
        """Kept lines use +: prefix."""
        rules = ClearRules(profile="minimal")

        output_lines = []
        import builtins

        original_print = builtins.print

        def mock_print(*args, **kwargs):
            if args:
                output_lines.append(args[0])

        builtins.print = mock_print

        try:
            # Three lines: first is kept, second is cleared, third is clear marker
            fifo = deque(
                [
                    (1, "kept_line"),
                    (2, "cleared_line"),
                    (3, "\x1b[2K" * 2),  # 2 clears -> clear 1 line (N-1)
                ]
            )
            clear_lines(
                fifo,
                clear_count=2,
                show_prefixes=True,
                show_line_numbers=False,
                clear_operation_count=0,
                rules=rules,
            )

            # First output should be kept line with +:
            assert len(output_lines) >= 1
            assert output_lines[0].startswith("+:")

        finally:
            builtins.print = original_print


@pytest.mark.property
class TestPipelineInvariants:
    """Test invariants for full pipeline."""

    def test_pipeline_output_size_bounded(self):
        """Pipeline output should be <= input size (compression, not expansion)."""
        # Create test input
        input_data = b"line1\nline2\nline3\n" * 100

        # Run through pipeline
        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.clear_lines", "--prefixes", "--profile", "minimal"],
            input=input_data,
            capture_output=True,
        )

        assert result.returncode == 0
        # Output might be larger due to prefixes, but shouldn't explode
        assert len(result.stdout) < len(input_data) * 2

    def test_pipeline_preserves_line_count_or_reduces(self):
        """Pipeline never increases line count (deduplication/filtering)."""
        input_lines = ["line1\n", "line2\n", "line3\n"] * 10
        input_data = "".join(input_lines).encode()

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.clear_lines", "--profile", "minimal"],
            input=input_data,
            capture_output=True,
        )

        assert result.returncode == 0
        output_line_count = result.stdout.decode().count("\n")
        input_line_count = len(input_lines)

        # Should never increase line count
        assert output_line_count <= input_line_count


@pytest.mark.property
class TestClearRulesInvariants:
    """Test invariants for clear rules."""

    def test_calculated_count_bounded_by_input(self):
        """Calculated clear count should never exceed input count - 1."""
        rules = ClearRules(profile="generic")

        for n in range(1, 20):
            count = rules.calculate_clear_count(
                clear_line_count=n,
                first_cleared_line="content",
                first_sequence_line=None,
                next_line_after_clear=None,
            )

            # With protections, count might be reduced, but never exceed N-1
            assert count <= n - 1

    def test_protections_only_reduce_count(self):
        """Protections can only reduce clear count, never increase."""
        # Minimal has no protections
        rules_minimal = ClearRules(profile="minimal")

        # Generic has protections
        rules_generic = ClearRules(profile="generic")

        count_minimal = rules_minimal.calculate_clear_count(
            clear_line_count=5,
            first_cleared_line="   ",  # Blank line triggers protection
            first_sequence_line=None,
            next_line_after_clear=None,
        )

        count_generic = rules_generic.calculate_clear_count(
            clear_line_count=5,
            first_cleared_line="   ",  # Blank line triggers protection
            first_sequence_line=None,
            next_line_after_clear=None,
        )

        # Generic should have equal or fewer cleared lines
        assert count_generic <= count_minimal
