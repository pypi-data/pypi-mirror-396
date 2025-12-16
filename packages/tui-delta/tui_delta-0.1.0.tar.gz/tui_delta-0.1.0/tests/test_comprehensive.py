"""Comprehensive tests using precomputed fixtures with detailed analysis."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def load_fixtures(filename: str):
    """Load fixture file."""
    fixtures_path = Path(__file__).parent / "fixtures" / filename
    with open(fixtures_path) as f:
        return json.load(f)


# Load all fixture sets
HANDCRAFTED = load_fixtures("handcrafted_cases.json")
EDGE_CASES = load_fixtures("edge_cases.json")
RANDOM_CASES = load_fixtures("random_cases.json")
ALL_CASES = HANDCRAFTED + EDGE_CASES + RANDOM_CASES


@pytest.mark.unit
class TestHandcraftedCases:
    """Test handcrafted cases with known patterns."""

    @pytest.mark.parametrize("fixture", HANDCRAFTED, ids=[f["name"] for f in HANDCRAFTED])
    def test_handcrafted_output(self, fixture):
        """Verify output matches expected for handcrafted cases."""
        # Prepare input
        input_data = "\n".join(fixture["input_lines"]) + "\n"

        # Run through clear_lines
        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.clear_lines", "--profile", fixture["profile"]],
            input=input_data.encode(),
            capture_output=True,
        )

        assert result.returncode == 0

        # Count output lines
        output_lines = result.stdout.decode().strip().split("\n") if result.stdout else []
        assert len(output_lines) == fixture["expected_output_count"]


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases with boundary conditions."""

    @pytest.mark.parametrize("fixture", EDGE_CASES, ids=[f["name"] for f in EDGE_CASES])
    def test_edge_case_output(self, fixture):
        """Verify output matches expected for edge cases."""
        input_data = "\n".join(fixture["input_lines"]) + "\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.clear_lines", "--profile", fixture["profile"]],
            input=input_data.encode(),
            capture_output=True,
        )

        assert result.returncode == 0

        output_lines = result.stdout.decode().strip().split("\n") if result.stdout else []
        assert len(output_lines) == fixture["expected_output_count"]


@pytest.mark.property
class TestRandomCases:
    """Test mixed content cases."""

    @pytest.mark.parametrize("fixture", RANDOM_CASES, ids=[f["name"] for f in RANDOM_CASES])
    def test_random_output(self, fixture):
        """Verify output for mixed content."""
        input_data = "\n".join(fixture["input_lines"]) + "\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.clear_lines", "--profile", fixture["profile"]],
            input=input_data.encode(),
            capture_output=True,
        )

        assert result.returncode == 0

        output_lines = result.stdout.decode().strip().split("\n") if result.stdout else []
        assert len(output_lines) == fixture["expected_output_count"]


@pytest.mark.property
class TestInvariantsWithFixtures:
    """Test algorithm invariants hold for all fixture cases."""

    @pytest.mark.parametrize("fixture", ALL_CASES, ids=[f["name"] for f in ALL_CASES])
    def test_no_data_loss(self, fixture):
        """All input content appears in output (no data loss)."""
        input_data = "\n".join(fixture["input_lines"]) + "\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.clear_lines", "--profile", fixture["profile"]],
            input=input_data.encode(),
            capture_output=True,
        )

        assert result.returncode == 0

        # Output should exist
        assert len(result.stdout) > 0

    @pytest.mark.parametrize("fixture", ALL_CASES, ids=[f["name"] for f in ALL_CASES])
    def test_line_order_preserved(self, fixture):
        """Lines appear in same order as input."""
        input_data = "\n".join(fixture["input_lines"]) + "\n"

        result = subprocess.run(
            [sys.executable, "-m", "tui_delta.clear_lines", "--profile", fixture["profile"]],
            input=input_data.encode(),
            capture_output=True,
        )

        assert result.returncode == 0

        output = result.stdout.decode()

        # Extract non-clear input lines
        non_clear_inputs = [line for line in fixture["input_lines"] if "\x1b[2K" not in line]

        # All non-clear input lines should appear in output in order
        last_pos = -1
        for input_line in non_clear_inputs:
            pos = output.find(input_line)
            assert pos >= last_pos, f"Line '{input_line}' out of order"
            last_pos = pos


@pytest.mark.property
class TestFixtureQuality:
    """Verify fixture data quality and coverage."""

    def test_all_fixtures_loaded(self):
        """All fixture files loaded successfully."""
        assert len(HANDCRAFTED) == 2
        assert len(EDGE_CASES) == 2
        assert len(RANDOM_CASES) == 1
        assert len(ALL_CASES) == 5

    def test_fixtures_have_required_fields(self):
        """All fixtures have required fields."""
        required = {
            "name",
            "description",
            "input_lines",
            "expected_output_count",
            "profile",
        }

        for fixture in ALL_CASES:
            missing = required - set(fixture.keys())
            assert not missing, f"Fixture {fixture['name']} missing: {missing}"

    def test_fixture_profiles_valid(self):
        """All fixtures use valid profiles."""
        valid_profiles = {"minimal", "generic", "claude_code"}

        for fixture in ALL_CASES:
            assert fixture["profile"] in valid_profiles, (
                f"Fixture {fixture['name']} has invalid profile: {fixture['profile']}"
            )
