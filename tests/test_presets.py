"""
Tests for preset environment files.
"""
import pytest
from pathlib import Path


class TestPresetFiles:
    """Test preset .env files."""

    def test_all_levels_exist(self, presets_dir):
        """Verify all 5 levels have preset files."""
        for level in range(5):
            preset_file = presets_dir / f"level-{level}.env"
            assert preset_file.exists(), f"Missing preset file: level-{level}.env"

    def test_preset_files_not_empty(self, all_preset_files):
        """Verify preset files are not empty."""
        for preset_file in all_preset_files:
            content = preset_file.read_text()
            assert len(content) > 0, f"Preset file is empty: {preset_file.name}"

    def test_presets_have_required_vars(self, all_preset_files):
        """Verify presets contain required environment variables."""
        required_vars = [
            "INCLUDE_POSTGRES",
            "INCLUDE_DAGSTER",
            "INCLUDE_SUPERSET",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
        ]

        for preset_file in all_preset_files:
            content = preset_file.read_text()
            for var in required_vars:
                assert var in content, f"Missing {var} in {preset_file.name}"

    def test_preset_syntax_valid(self, all_preset_files):
        """Verify preset files have valid KEY=VALUE syntax."""
        for preset_file in all_preset_files:
            lines = preset_file.read_text().splitlines()
            for i, line in enumerate(lines, 1):
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Must contain = sign
                assert "=" in line, f"Invalid syntax at line {i} in {preset_file.name}: {line}"

    def test_level_0_minimal(self, presets_dir):
        """Verify level 0 has minimal components (DuckDB + dbt only)."""
        level_0 = presets_dir / "level-0.env"
        if level_0.exists():
            content = level_0.read_text()
            # Level 0 should have most services disabled
            assert "INCLUDE_KAFKA=false" in content or "INCLUDE_KAFKA" not in content
            assert "INCLUDE_FLINK=false" in content or "INCLUDE_FLINK" not in content

    def test_higher_levels_have_more_services(self, presets_dir):
        """Verify higher levels include more services."""
        def count_enabled(content):
            return content.count("=true")

        prev_count = 0
        for level in range(5):
            preset_file = presets_dir / f"level-{level}.env"
            if preset_file.exists():
                content = preset_file.read_text()
                count = count_enabled(content)
                # Level should have at least as many services as previous
                # (except level 0 which is special)
                if level > 0:
                    assert count >= prev_count, \
                        f"Level {level} has fewer services ({count}) than level {level-1} ({prev_count})"
                prev_count = count

    def test_no_hardcoded_production_secrets(self, all_preset_files):
        """Warn about default secrets that should be changed in production."""
        dangerous_patterns = [
            "password123",
            "secret123",
            "admin123",
        ]

        for preset_file in all_preset_files:
            content = preset_file.read_text().lower()
            for pattern in dangerous_patterns:
                assert pattern not in content, \
                    f"Found dangerous default password '{pattern}' in {preset_file.name}"
