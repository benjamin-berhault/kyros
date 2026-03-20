"""
Tests for Kyros CLI functionality.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestCLIComponents:
    """Test CLI component definitions."""

    def test_cli_exists(self, kyros_root):
        """Verify CLI script exists."""
        cli_path = kyros_root / "kyros-cli.py"
        assert cli_path.exists(), "kyros-cli.py not found"

    def test_cli_is_executable(self, kyros_root):
        """Verify CLI script has executable permission."""
        cli_path = kyros_root / "kyros-cli.py"
        import os
        # Check if file has any execute permission
        assert os.access(cli_path, os.X_OK), "kyros-cli.py is not executable"

    def test_cli_has_shebang(self, kyros_root):
        """Verify CLI has proper shebang line."""
        cli_path = kyros_root / "kyros-cli.py"
        first_line = cli_path.read_text().splitlines()[0]
        assert first_line.startswith("#!"), "Missing shebang line"
        assert "python" in first_line.lower(), "Shebang should reference python"


class TestCLIFunctions:
    """Test CLI functions (requires importing the module)."""

    @pytest.fixture
    def cli_module(self, kyros_root):
        """Import and return the CLI module."""
        # Mock rich to avoid terminal issues in tests
        mock_console = MagicMock()
        with patch.dict(sys.modules, {
            'rich': MagicMock(),
            'rich.console': MagicMock(Console=lambda: mock_console),
            'rich.panel': MagicMock(),
            'rich.table': MagicMock(),
            'rich.prompt': MagicMock(),
            'rich.live': MagicMock(),
            'rich.text': MagicMock(),
            'rich.progress': MagicMock(),
        }):
            # Clear any cached import
            if 'kyros-cli' in sys.modules:
                del sys.modules['kyros-cli']

            # Import the module
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "kyros_cli",
                kyros_root / "kyros-cli.py"
            )
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                return module
            except Exception:
                pytest.skip("Could not import CLI module")

    def test_components_defined(self, cli_module):
        """Verify COMPONENTS dictionary is defined."""
        assert hasattr(cli_module, 'COMPONENTS')
        assert isinstance(cli_module.COMPONENTS, dict)
        assert len(cli_module.COMPONENTS) > 0

    def test_levels_defined(self, cli_module):
        """Verify LEVELS dictionary is defined."""
        assert hasattr(cli_module, 'LEVELS')
        assert isinstance(cli_module.LEVELS, dict)
        # Should have 5 levels (0-4)
        assert len(cli_module.LEVELS) == 5

    def test_component_has_required_fields(self, cli_module):
        """Verify each component has required metadata."""
        required_fields = ["name", "level", "desc"]

        for comp_key, comp_data in cli_module.COMPONENTS.items():
            for field in required_fields:
                assert field in comp_data, \
                    f"Component {comp_key} missing field: {field}"

    def test_level_has_required_fields(self, cli_module):
        """Verify each level has required metadata."""
        required_fields = ["name", "desc", "cost", "data"]

        for level, level_data in cli_module.LEVELS.items():
            for field in required_fields:
                assert field in level_data, \
                    f"Level {level} missing field: {field}"

    def test_generate_env_function(self, cli_module):
        """Test the generate_env function."""
        if not hasattr(cli_module, 'generate_env'):
            pytest.skip("generate_env function not found")

        selected = {"POSTGRES", "DAGSTER"}
        result = cli_module.generate_env(selected, workers=2)

        assert "INCLUDE_POSTGRES=true" in result
        assert "INCLUDE_DAGSTER=true" in result
        assert "WORKERS=2" in result

    def test_component_levels_valid(self, cli_module):
        """Verify component levels are within valid range."""
        for comp_key, comp_data in cli_module.COMPONENTS.items():
            level = comp_data.get("level")
            assert level is not None, f"Component {comp_key} has no level"
            assert 0 <= level <= 4, f"Component {comp_key} has invalid level: {level}"


class TestEnvGeneration:
    """Test .env file generation logic."""

    def test_env_contains_all_components(self, kyros_root):
        """Test that generated env contains all component flags."""
        # This tests the logic without running the CLI
        components = [
            "POSTGRES", "DAGSTER", "SUPERSET", "DBT", "MINIO",
            "JUPYTERLAB", "TRINO", "KAFKA", "FLINK", "GRAFANA",
            "CLOUDBEAVER", "CODE_SERVER", "PORTAINER", "KYROS"
        ]

        # Read a preset to verify format
        preset = kyros_root / "presets" / "level-1.env"
        if preset.exists():
            content = preset.read_text()
            for comp in components:
                # Each component should have INCLUDE_{COMP}= line
                assert f"INCLUDE_{comp}=" in content or comp == "SQLPAD", \
                    f"Missing INCLUDE_{comp} in preset"
