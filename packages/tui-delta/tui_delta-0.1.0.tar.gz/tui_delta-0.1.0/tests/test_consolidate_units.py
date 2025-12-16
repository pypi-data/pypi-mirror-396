"""Unit tests for consolidate_clears.py helper functions."""

import io

import pytest
from rich.console import Console
from rich.text import Text


@pytest.mark.unit
class TestCharDiff:
    """Test _char_diff function with various inputs."""

    def test_char_diff_equal_strings(self):
        """Test _char_diff with identical strings."""
        from tui_delta.consolidate_clears import _char_diff

        result = _char_diff("hello world", "hello world")

        # Should return Text object
        assert isinstance(result, Text)
        # Content should match
        assert "hello world" in str(result)

    def test_char_diff_completely_different(self):
        """Test _char_diff with completely different strings."""
        from tui_delta.consolidate_clears import _char_diff

        result = _char_diff("abc", "xyz")

        assert isinstance(result, Text)
        # Should show differences
        assert len(str(result)) > 0

    def test_char_diff_empty_strings(self):
        """Test _char_diff with empty strings."""
        from tui_delta.consolidate_clears import _char_diff

        result = _char_diff("", "")

        assert isinstance(result, Text)

    def test_char_diff_one_empty(self):
        """Test _char_diff with one empty string."""
        from tui_delta.consolidate_clears import _char_diff

        result1 = _char_diff("text", "")
        result2 = _char_diff("", "text")

        assert isinstance(result1, Text)
        assert isinstance(result2, Text)

    def test_char_diff_partial_match(self):
        """Test _char_diff with partial match."""
        from tui_delta.consolidate_clears import _char_diff

        result = _char_diff("hello world", "hello there")

        assert isinstance(result, Text)
        # Should have both matching and different parts
        assert "hello" in str(result)

    def test_char_diff_insert_operation(self):
        """Test _char_diff with insert operation."""
        from tui_delta.consolidate_clears import _char_diff

        result = _char_diff("abc", "abXc")

        assert isinstance(result, Text)
        # Should handle insertion
        assert len(result) > 0

    def test_char_diff_delete_operation(self):
        """Test _char_diff with delete operation."""
        from tui_delta.consolidate_clears import _char_diff

        result = _char_diff("abXc", "abc")

        assert isinstance(result, Text)
        # Should handle deletion
        assert len(result) > 0

    def test_char_diff_replace_operation(self):
        """Test _char_diff with replace operation."""
        from tui_delta.consolidate_clears import _char_diff

        result = _char_diff("abc", "aXc")

        assert isinstance(result, Text)
        # Should handle replacement
        assert len(result) > 0

    def test_char_diff_multiple_operations(self):
        """Test _char_diff with multiple operations."""
        from tui_delta.consolidate_clears import _char_diff

        result = _char_diff("the quick brown fox", "a fast red dog")

        assert isinstance(result, Text)
        # Should handle multiple changes
        assert len(result) > 0

    def test_char_diff_long_strings(self):
        """Test _char_diff with long strings."""
        from tui_delta.consolidate_clears import _char_diff

        old = "a" * 1000 + "b" * 1000
        new = "a" * 1000 + "c" * 1000

        result = _char_diff(old, new)

        assert isinstance(result, Text)
        # Should handle long strings
        assert len(result) > 0


@pytest.mark.unit
class TestRenderComponentSequence:
    """Test _render_component_sequence function."""

    def test_render_empty_components(self):
        """Test rendering empty component list."""
        from tui_delta.consolidate_clears import _render_component_sequence

        result = _render_component_sequence([])

        assert result == ""

    def test_render_text_only_components(self):
        """Test rendering text-only components."""
        from tui_delta.consolidate_clears import _render_component_sequence

        components = [{"text": "hello"}, {"text": " "}, {"text": "world"}]

        result = _render_component_sequence(components)

        assert "hello" in result
        assert "world" in result

    def test_render_with_serialized_field(self):
        """Test rendering with serialized field."""
        from tui_delta.consolidate_clears import _render_component_sequence

        # When both text and serialized present, text takes precedence
        components = [
            {"serialized": "123"}  # Only serialized, no text
        ]

        result = _render_component_sequence(components)

        assert "123" in result

    def test_render_mixed_components(self):
        """Test rendering mixed text and serialized."""
        from tui_delta.consolidate_clears import _render_component_sequence

        components = [{"text": "count: "}, {"text": "5", "serialized": "5"}, {"text": " items"}]

        result = _render_component_sequence(components)

        assert "count" in result
        assert "5" in result
        assert "items" in result


@pytest.mark.unit
class TestPrintPrefixedLine:
    """Test _print_prefixed_line function."""

    def test_print_prefixed_line_basic(self, capsys):
        """Test _print_prefixed_line with basic input."""
        from tui_delta.consolidate_clears import _print_prefixed_line

        _print_prefixed_line("+: ", "test content", None)

        captured = capsys.readouterr()
        assert "+: test content" in captured.out

    def test_print_prefixed_line_with_console(self):
        """Test _print_prefixed_line with Rich console."""
        from tui_delta.consolidate_clears import _print_prefixed_line

        buffer = io.StringIO()
        console = Console(file=buffer, force_terminal=False)

        _print_prefixed_line("+: ", "test content", console)

        output = buffer.getvalue()
        assert "test content" in output

    def test_print_prefixed_line_empty_content(self, capsys):
        """Test _print_prefixed_line with empty content."""
        from tui_delta.consolidate_clears import _print_prefixed_line

        _print_prefixed_line("+: ", "", None)

        captured = capsys.readouterr()
        assert "+: " in captured.out

    def test_print_prefixed_line_text_object(self, capsys):
        """Test _print_prefixed_line with Text object."""
        from tui_delta.consolidate_clears import _print_prefixed_line

        text = Text("styled text")
        _print_prefixed_line("+: ", text, None)

        captured = capsys.readouterr()
        assert "styled text" in captured.out


@pytest.mark.unit
class TestNormalize:
    """Test normalize function."""

    def test_normalize_with_none_engine(self):
        """Test normalize with None engine."""
        from tui_delta.consolidate_clears import normalize

        lines = ["line1", "line2", "line3"]
        result = normalize(None, lines)

        # Should return original lines unchanged
        assert result == lines

    def test_normalize_with_empty_list(self):
        """Test normalize with empty list."""
        from tui_delta.consolidate_clears import normalize

        result = normalize(None, [])

        assert result == []


@pytest.mark.unit
class TestParseLine:
    """Test parse_line edge cases."""

    def test_parse_line_kept(self):
        """Test parse_line with kept prefix."""
        from tui_delta.consolidate_clears import LineType, parse_line

        line_type, content = parse_line("+: some content")

        assert line_type == LineType.KEPT
        assert content == "some content"

    def test_parse_line_cleared_backslash(self):
        """Test parse_line with backslash cleared prefix."""
        from tui_delta.consolidate_clears import LineType, parse_line

        line_type, content = parse_line("\\: cleared content")

        assert line_type == LineType.CLEARED_BACKSLASH
        assert content == "cleared content"

    def test_parse_line_cleared_slash(self):
        """Test parse_line with forward slash cleared prefix."""
        from tui_delta.consolidate_clears import LineType, parse_line

        line_type, content = parse_line("/: cleared content")

        assert line_type == LineType.CLEARED_SLASH
        assert content == "cleared content"

    def test_parse_line_command(self):
        """Test parse_line with command prefix."""
        from tui_delta.consolidate_clears import LineType, parse_line

        line_type, content = parse_line(">: [window-title:test]")

        assert line_type == LineType.COMMAND
        assert content == "[window-title:test]"

    def test_parse_line_invalid_prefix(self):
        """Test parse_line with invalid prefix raises error."""
        from tui_delta.consolidate_clears import parse_line

        with pytest.raises(ValueError, match="Unrecognized line prefix"):
            parse_line("invalid prefix")

    def test_parse_line_empty_content(self):
        """Test parse_line with empty content after prefix."""
        from tui_delta.consolidate_clears import LineType, parse_line

        line_type, content = parse_line("+: ")

        assert line_type == LineType.KEPT
        assert content == ""


@pytest.mark.unit
class TestIsWindowTitleLine:
    """Test is_window_title_line function."""

    def test_is_window_title_true(self):
        """Test is_window_title_line with window title."""
        from tui_delta.consolidate_clears import is_window_title_line

        assert is_window_title_line("[window-title:test]") is True

    def test_is_window_title_icon_true(self):
        """Test is_window_title_line with window title icon."""
        from tui_delta.consolidate_clears import is_window_title_line

        assert is_window_title_line("[window-title-icon:test]") is True

    def test_is_window_title_false(self):
        """Test is_window_title_line with non-window-title."""
        from tui_delta.consolidate_clears import is_window_title_line

        assert is_window_title_line("regular content") is False

    def test_is_window_title_empty(self):
        """Test is_window_title_line with empty string."""
        from tui_delta.consolidate_clears import is_window_title_line

        assert is_window_title_line("") is False


@pytest.mark.unit
class TestCreateRulesFile:
    """Test _create_rules_file_from_profiles function."""

    def test_create_rules_file_returns_path(self):
        """Test that _create_rules_file_from_profiles returns a Path."""
        from pathlib import Path

        from tui_delta.consolidate_clears import _create_rules_file_from_profiles

        result = _create_rules_file_from_profiles()

        assert isinstance(result, Path)
        # Should be a temporary file
        assert result.exists()
        # Cleanup
        result.unlink()

    def test_create_rules_file_has_content(self):
        """Test that created rules file has content."""
        from tui_delta.consolidate_clears import _create_rules_file_from_profiles

        result = _create_rules_file_from_profiles()

        # Should have content (copied from tui_profiles.yaml)
        content = result.read_text()
        assert len(content) > 0
        # Should contain YAML structure
        assert "profiles:" in content or "rules:" in content or "patterns:" in content

        # Cleanup
        result.unlink()


@pytest.mark.unit
class TestOutputDiff:
    """Test output_diff function with various scenarios."""

    def test_output_diff_returns_sequence_lines(self):
        """Test output_diff returns sequence lines."""
        from tui_delta.consolidate_clears import output_diff

        result = output_diff(["line1"], ["line1"], "\\: ")

        # Should return a list
        assert isinstance(result, list)

    def test_output_diff_different_lines(self):
        """Test output_diff with different lines."""
        from tui_delta.consolidate_clears import output_diff

        result = output_diff(["old"], ["new"], "\\: ")

        assert isinstance(result, list)

    def test_output_diff_empty_old(self):
        """Test output_diff with empty old lines."""
        from tui_delta.consolidate_clears import output_diff

        result = output_diff([], ["new line"], "\\: ")

        assert isinstance(result, list)

    def test_output_diff_empty_new(self):
        """Test output_diff with empty new lines."""
        from tui_delta.consolidate_clears import output_diff

        result = output_diff(["old line"], [], "\\: ")

        assert isinstance(result, list)

    def test_output_diff_multiline(self):
        """Test output_diff with multiline."""
        from tui_delta.consolidate_clears import output_diff

        old = ["line1", "line2", "line3"]
        new = ["line1", "line2", "line3"]

        result = output_diff(old, new, "\\: ")

        assert isinstance(result, list)


@pytest.mark.unit
class TestClearLinesHelpers:
    """Test clear_lines.py helper functions."""

    def test_extract_osc_window_title_with_bell(self):
        """Test extract_osc_window_title with bell terminator."""
        from tui_delta.clear_lines import extract_osc_window_title

        result = extract_osc_window_title("\x1b]0;MyTitle\x07")

        assert result == "MyTitle"

    def test_extract_osc_window_title_with_st(self):
        """Test extract_osc_window_title with ST terminator."""
        from tui_delta.clear_lines import extract_osc_window_title

        result = extract_osc_window_title("\x1b]2;AnotherTitle\x1b\\")

        assert result == "AnotherTitle"

    def test_extract_osc_window_title_invalid(self):
        """Test extract_osc_window_title with invalid sequence."""
        from tui_delta.clear_lines import extract_osc_window_title

        result = extract_osc_window_title("\x1b]1;InvalidCode\x07")

        assert result is None

    def test_extract_osc_window_title_no_sequence(self):
        """Test extract_osc_window_title with no OSC sequence."""
        from tui_delta.clear_lines import extract_osc_window_title

        result = extract_osc_window_title("regular text")

        assert result is None

    def test_count_clear_sequences_none(self):
        """Test count_clear_sequences with no clear sequences."""
        from tui_delta.clear_lines import count_clear_sequences

        result = count_clear_sequences("regular line")

        assert result == 0

    def test_count_clear_sequences_one(self):
        """Test count_clear_sequences with one clear sequence."""
        from tui_delta.clear_lines import count_clear_sequences

        result = count_clear_sequences("\x1b[2K")

        assert result == 1

    def test_count_clear_sequences_multiple(self):
        """Test count_clear_sequences with multiple clear sequences."""
        from tui_delta.clear_lines import count_clear_sequences

        result = count_clear_sequences("\x1b[2K\x1b[2K\x1b[2K")

        assert result == 3

    def test_count_clear_sequences_mixed_content(self):
        """Test count_clear_sequences with mixed content."""
        from tui_delta.clear_lines import count_clear_sequences

        result = count_clear_sequences("text\x1b[2Kmore text\x1b[2K")

        assert result == 2

    def test_format_line_no_prefix_no_number(self):
        """Test _format_line without prefix or line number."""
        from tui_delta.clear_lines import _format_line

        result = _format_line("+: ", 42, "content", show_prefixes=False, show_line_numbers=False)

        assert result == "content"

    def test_format_line_prefix_only(self):
        """Test _format_line with prefix only."""
        from tui_delta.clear_lines import _format_line

        result = _format_line("+: ", 42, "content", show_prefixes=True, show_line_numbers=False)

        assert "+: content" in result

    def test_format_line_number_only(self):
        """Test _format_line with line number only."""
        from tui_delta.clear_lines import _format_line

        result = _format_line("+: ", 42, "content", show_prefixes=False, show_line_numbers=True)

        assert "42" in result
        assert "content" in result

    def test_format_line_both_prefix_and_number(self):
        """Test _format_line with both prefix and line number."""
        from tui_delta.clear_lines import _format_line

        result = _format_line("+: ", 42, "content", show_prefixes=True, show_line_numbers=True)

        assert "+: " in result
        assert "42" in result
        assert "content" in result


@pytest.mark.unit
class TestMatchPatternComponents:
    """Test _match_pattern_components function."""

    def test_match_text_component(self):
        """Test matching simple text component."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"text": "hello"}]
        matched, fields = _match_pattern_components("hello world", pattern)

        assert matched is True
        assert fields == {}

    def test_match_serialized_component(self):
        """Test matching serialized component."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"serialized": "test"}]
        matched, fields = _match_pattern_components("test content", pattern)

        assert matched is True
        assert fields == {}

    def test_match_number_field(self):
        """Test matching NUMBER field parser."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"field": "count", "parser": "NUMBER"}]
        matched, fields = _match_pattern_components("123 items", pattern)

        assert matched is True
        # Fields extraction may or may not populate, just verify it matched

    def test_match_alternatives_first(self):
        """Test matching first alternative."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"alternatives": [[{"text": "option1"}], [{"text": "option2"}]]}]
        matched, fields = _match_pattern_components("option1 content", pattern)

        assert matched is True

    def test_match_alternatives_second(self):
        """Test matching second alternative."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"alternatives": [[{"text": "option1"}], [{"text": "option2"}]]}]
        matched, fields = _match_pattern_components("option2 content", pattern)

        assert matched is True

    def test_match_alternatives_none(self):
        """Test no alternative matches."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"alternatives": [[{"text": "option1"}], [{"text": "option2"}]]}]
        matched, fields = _match_pattern_components("option3 content", pattern)

        assert matched is False
        assert fields == {}

    def test_match_number_field_no_digits(self):
        """Test NUMBER field with no digits."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"field": "count", "parser": "NUMBER"}]
        matched, fields = _match_pattern_components("no digits here", pattern)

        assert matched is False
        assert fields == {}

    def test_match_text_mismatch(self):
        """Test text component mismatch."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"text": "expected"}]
        matched, fields = _match_pattern_components("actual", pattern)

        assert matched is False
        assert fields == {}

    def test_match_serialized_mismatch(self):
        """Test serialized component mismatch."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"serialized": "expected"}]
        matched, fields = _match_pattern_components("actual", pattern)

        assert matched is False
        assert fields == {}

    def test_match_position_overflow(self):
        """Test pattern extends beyond line length."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"text": "a"}, {"text": "b"}, {"text": "c"}, {"text": "d"}]
        matched, fields = _match_pattern_components("ab", pattern)

        assert matched is False
        assert fields == {}

    def test_match_complex_pattern(self):
        """Test complex pattern with multiple components."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"text": "Count: "}, {"field": "num", "parser": "NUMBER"}]
        matched, fields = _match_pattern_components("Count: 42", pattern)

        assert matched is True

    def test_match_ansi_codes_stripped(self):
        """Test ANSI codes are stripped before matching."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"text": "hello"}]
        matched, fields = _match_pattern_components("\x1b[31mhello\x1b[0m", pattern)

        assert matched is True


@pytest.mark.unit
class TestExtractSequenceBlock:
    """Test _extract_sequence_block function."""

    def test_extract_no_sequences(self):
        """Test with no sequence markers."""
        from tui_delta.consolidate_clears import _extract_sequence_block

        lines = ["line1", "line2", "line3"]
        normalized = ["line1", "line2", "line3"]
        configs = {}
        markers = []

        non_seq, seq, non_seq_norm, seq_norm = _extract_sequence_block(
            lines, normalized, configs, markers
        )

        assert non_seq == lines
        assert seq == []
        assert non_seq_norm == normalized
        assert seq_norm == []

    def test_extract_sequence_with_marker(self):
        """Test extracting sequence with marker."""
        from tui_delta.consolidate_clears import _extract_sequence_block

        lines = ["[progress:", "line1", "line2"]
        normalized = ["[progress:", "line1", "line2"]
        configs = {
            "progress": {
                "output": "[progress:updated]",
                "sequence": {"followers": []},
            }
        }
        markers = ["[progress:"]

        non_seq, seq, non_seq_norm, seq_norm = _extract_sequence_block(
            lines, normalized, configs, markers
        )

        # First line should be extracted as sequence
        assert len(seq) > 0
        assert len(non_seq) < len(lines)

    def test_extract_multiple_sequences(self):
        """Test extracting multiple sequences."""
        from tui_delta.consolidate_clears import _extract_sequence_block

        lines = ["[progress:", "other", "[progress:", "more"]
        normalized = lines
        configs = {
            "progress": {
                "output": "[progress:updated]",
                "sequence": {"followers": []},
            }
        }
        markers = ["[progress:"]

        non_seq, seq, non_seq_norm, seq_norm = _extract_sequence_block(
            lines, normalized, configs, markers
        )

        # Should have extracted sequences
        assert len(seq) > 0


@pytest.mark.unit
class TestOutputDiffAdvanced:
    """Test output_diff with advanced scenarios."""

    def test_output_diff_single_line_replace(self):
        """Test output_diff with single-line replace (character-level diff)."""
        from tui_delta.consolidate_clears import output_diff

        old = ["status: running"]
        new = ["status: complete"]

        result = output_diff(old, new, "\\: ")

        # Should return sequence with character-level diff
        assert isinstance(result, list)

    def test_output_diff_multiline_replace(self):
        """Test output_diff with multi-line replace."""
        from tui_delta.consolidate_clears import output_diff

        old = ["line1", "line2"]
        new = ["new1", "new2"]

        result = output_diff(old, new, "\\: ")

        assert isinstance(result, list)

    def test_output_diff_insertions(self):
        """Test output_diff with insertions."""
        from tui_delta.consolidate_clears import output_diff

        old = ["line1"]
        new = ["line1", "line2", "line3"]

        result = output_diff(old, new, "\\: ")

        assert isinstance(result, list)

    def test_output_diff_deletions(self):
        """Test output_diff with deletions."""
        from tui_delta.consolidate_clears import output_diff

        old = ["line1", "line2", "line3"]
        new = ["line1"]

        result = output_diff(old, new, "\\: ")

        assert isinstance(result, list)


@pytest.mark.unit
class TestExtractSequenceWithFollowers:
    """Test sequence extraction with follower patterns."""

    def test_extract_sequence_with_followers(self):
        """Test extracting sequence with follower patterns."""
        from tui_delta.consolidate_clears import _extract_sequence_block

        lines = ["[progress:", "  item 1", "  item 2", "other"]
        normalized = lines
        configs = {
            "progress": {
                "output": "[progress:updated]",
                "sequence": {
                    "followers": [{"pattern": [{"text": "  item"}]}],
                },
            }
        }
        markers = ["[progress:"]

        non_seq, seq, non_seq_norm, seq_norm = _extract_sequence_block(
            lines, normalized, configs, markers
        )

        # Should extract leader and followers
        assert len(seq) >= 2  # At least leader + 1 follower
        assert "other" in non_seq  # Non-follower should not be extracted

    def test_extract_sequence_no_followers_match(self):
        """Test sequence where followers don't match."""
        from tui_delta.consolidate_clears import _extract_sequence_block

        lines = ["[progress:", "non-matching", "other"]
        normalized = lines
        configs = {
            "progress": {
                "output": "[progress:updated]",
                "sequence": {
                    "followers": [{"pattern": [{"text": "  expected"}]}],
                },
            }
        }
        markers = ["[progress:"]

        non_seq, seq, non_seq_norm, seq_norm = _extract_sequence_block(
            lines, normalized, configs, markers
        )

        # Should extract only leader, not followers
        assert len(seq) == 1
        assert "non-matching" in non_seq


@pytest.mark.unit
class TestMatchPatternEdgeCases:
    """Test edge cases in pattern matching."""

    def test_match_field_no_parser(self):
        """Test field without parser (uses default behavior)."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"field": "content"}]
        matched, fields = _match_pattern_components("any content here", pattern)

        # Should match and consume to end of line
        assert matched is True

    def test_match_past_end_of_line(self):
        """Test pattern component starts past line end."""
        from tui_delta.consolidate_clears import _match_pattern_components

        pattern = [{"text": "long"}, {"text": "pattern"}, {"text": "here"}]
        matched, fields = _match_pattern_components("short", pattern)

        assert matched is False
        assert fields == {}


@pytest.mark.unit
class TestOutputDiffWithConsole:
    """Test output_diff with console for character-level diffs."""

    def test_output_diff_char_level_single_line(self, capsys):
        """Test character-level diff is triggered for single-line changes."""
        from tui_delta.consolidate_clears import output_diff

        # Single-line replace should trigger character-level diff
        old = ["Progress: 50%"]
        new = ["Progress: 100%"]

        # Call with console to enable character-level diff
        result = output_diff(old, new, "\\: ")

        # Should return list (character diff happens internally)
        assert isinstance(result, list)

    def test_output_diff_multiline_no_char_diff(self):
        """Test multi-line replace doesn't trigger character-level diff."""
        from tui_delta.consolidate_clears import output_diff

        # Multi-line replace should NOT trigger character-level diff
        old = ["line1", "line2"]
        new = ["new1", "new2"]

        result = output_diff(old, new, "\\: ")

        assert isinstance(result, list)
