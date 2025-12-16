#!/usr/bin/env python3
"""
Clear rules configuration loader and evaluator.

Loads rules from YAML configuration file and applies them to determine
which lines should be cleared during a clear operation.
"""

import re
from pathlib import Path
from typing import Any, Optional

import yaml


class ClearRules:
    """Manages clear operation rules loaded from YAML configuration"""

    def __init__(self, config_path: Optional[Path] = None, profile: Optional[str] = None):
        """
        Initialize clear rules from configuration file.

        Args:
            config_path: Path to YAML config file (defaults to tui_profiles.yaml,
                        falls back to clear_rules.yaml for backward compatibility)
            profile: Profile name to use (defaults to config's default_profile)
        """
        if config_path is None:
            # Try new unified format first, fall back to old format
            unified_path = Path(__file__).parent / "tui_profiles.yaml"
            old_path = Path(__file__).parent / "clear_rules.yaml"
            config_path = unified_path if unified_path.exists() else old_path

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Determine which profile to use
        profile_name = profile or self.config.get("default_profile", "claude_code")
        profile_config = self.config["profiles"].get(profile_name)

        if not profile_config:
            raise ValueError(f"Profile '{profile_name}' not found in configuration")

        # Load enabled protections for this profile
        # Support both old format ('protections') and new format ('clear_protections')
        protection_key = (
            "clear_protections" if "clear_protections" in profile_config else "protections"
        )
        enabled_protection_names = set(profile_config[protection_key])

        # Load protection definitions
        # Support both old format ('protections') and new format ('clear_protections')
        protections_key = (
            "clear_protections" if "clear_protections" in self.config else "protections"
        )
        if isinstance(self.config[protections_key], list):
            # Old format: list of protection objects with 'name' field
            self.protections = [
                p for p in self.config[protections_key] if p["name"] in enabled_protection_names
            ]
        else:
            # New format: dict of protection_name -> protection_config
            self.protections = [
                {**v, "name": k}
                for k, v in self.config[protections_key].items()
                if k in enabled_protection_names
            ]

    def calculate_clear_count(
        self,
        clear_line_count: int,
        first_cleared_line: Optional[str],
        first_sequence_line: Optional[str],
        next_line_after_clear: Optional[str],
    ) -> int:
        """
        Calculate how many lines to clear based on rules.

        Args:
            clear_line_count: Number of [clear_line] instances (N)
            first_cleared_line: Content of first line that would be cleared (boundary)
            first_sequence_line: Content of first line in sequence (after previous clear)
            next_line_after_clear: Content of next line after current clear operation

        Returns:
            Number of lines to clear (excluding the clear marker line itself)
        """
        # Start with base formula: N - 1
        clear_count = clear_line_count - 1

        # Apply each protection rule
        for protection in self.protections:
            if not protection.get("enabled", True):
                continue

            condition = protection["condition"]
            condition_type = condition["type"]

            # Evaluate condition
            if condition_type == "first_cleared_line_matches":
                if first_cleared_line is not None:
                    pattern = condition["pattern"]
                    if re.match(pattern, first_cleared_line):
                        clear_count -= protection.get("reduction", 1)

            elif condition_type == "first_sequence_line_and_next_line_differ":
                if first_sequence_line is not None:
                    pattern = condition["first_line_pattern"]
                    # Check if first sequence line matches pattern
                    if pattern in first_sequence_line:  # Simple substring match for now
                        # Check if next line differs
                        if (
                            next_line_after_clear is None
                            or next_line_after_clear.strip() != first_sequence_line.strip()
                        ):
                            clear_count -= protection.get("reduction", 1)

            # Ensure clear_count doesn't go negative
            clear_count = max(0, clear_count)

        return clear_count

    @staticmethod
    def list_profiles(config_path: Optional[Path] = None) -> dict[str, str]:
        """
        List available profiles and their descriptions.

        Args:
            config_path: Path to YAML config file

        Returns:
            Dictionary mapping profile names to descriptions
        """
        if config_path is None:
            # Try new unified format first, fall back to old format
            unified_path = Path(__file__).parent / "tui_profiles.yaml"
            old_path = Path(__file__).parent / "clear_rules.yaml"
            config_path = unified_path if unified_path.exists() else old_path

        with open(config_path) as f:
            config = yaml.safe_load(f)

        return {
            name: profile.get("description", "") for name, profile in config["profiles"].items()
        }

    @staticmethod
    def get_profile_config(
        profile: Optional[str] = None, config_path: Optional[Path] = None
    ) -> dict[str, Any]:
        """
        Get the full configuration for a profile.

        Args:
            profile: Profile name (defaults to default_profile from config)
            config_path: Path to YAML config file

        Returns:
            Profile configuration dictionary
        """
        if config_path is None:
            # Try new unified format first, fall back to old format
            unified_path = Path(__file__).parent / "tui_profiles.yaml"
            old_path = Path(__file__).parent / "clear_rules.yaml"
            config_path = unified_path if unified_path.exists() else old_path

        with open(config_path) as f:
            config = yaml.safe_load(f)

        profile_name = profile or config.get("default_profile", "claude_code")
        profile_config = config["profiles"].get(profile_name)

        if not profile_config:
            raise ValueError(f"Profile '{profile_name}' not found in configuration")

        return profile_config
