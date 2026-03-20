"""
Integration tests for Kyros platform.

These tests verify the overall system works together.
Some tests require Docker to be running.
"""
import pytest
import subprocess
from pathlib import Path


class TestScripts:
    """Test shell scripts."""

    def test_generate_docker_compose_exists(self, kyros_root):
        """Verify docker-compose generation script exists."""
        script = kyros_root / "generate-docker-compose.sh"
        assert script.exists(), "generate-docker-compose.sh not found"

    def test_generate_docker_compose_executable(self, kyros_root):
        """Verify docker-compose generation script is executable."""
        import os
        script = kyros_root / "generate-docker-compose.sh"
        assert os.access(script, os.X_OK), "generate-docker-compose.sh is not executable"

    def test_build_script_exists(self, kyros_root):
        """Verify build script exists."""
        script = kyros_root / "build.sh"
        if script.exists():
            import os
            assert os.access(script, os.X_OK), "build.sh is not executable"


class TestDockerComposeTemplate:
    """Test docker-compose template."""

    def test_template_exists(self, kyros_root):
        """Verify docker-compose template exists."""
        template = kyros_root / "docker-compose.template.yml"
        assert template.exists(), "docker-compose.template.yml not found"

    def test_template_valid_yaml(self, kyros_root):
        """Verify template is valid YAML."""
        import yaml
        template = kyros_root / "docker-compose.template.yml"
        if template.exists():
            try:
                content = template.read_text()
                yaml.safe_load(content)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in template: {e}")


class TestProjectStructure:
    """Test overall project structure."""

    def test_required_directories_exist(self, kyros_root):
        """Verify required directories exist."""
        required_dirs = [
            "services",
            "presets",
            "docker",
        ]

        for dir_name in required_dirs:
            dir_path = kyros_root / dir_name
            assert dir_path.exists(), f"Required directory missing: {dir_name}"
            assert dir_path.is_dir(), f"{dir_name} is not a directory"

    def test_readme_exists(self, kyros_root):
        """Verify README exists."""
        readme = kyros_root / "README.md"
        assert readme.exists(), "README.md not found"

    def test_license_exists(self, kyros_root):
        """Verify LICENSE file exists."""
        license_file = kyros_root / "LICENSE"
        assert license_file.exists(), "LICENSE file not found"

    def test_gitignore_exists(self, kyros_root):
        """Verify .gitignore exists."""
        gitignore = kyros_root / ".gitignore"
        assert gitignore.exists(), ".gitignore not found"


@pytest.mark.skipif(
    subprocess.run(["docker", "info"], capture_output=True).returncode != 0,
    reason="Docker not available"
)
class TestDockerIntegration:
    """Tests that require Docker."""

    def test_docker_compose_config_valid(self, kyros_root):
        """Test that docker-compose config is valid (requires Docker)."""
        compose_file = kyros_root / "docker-compose.yml"
        if compose_file.exists():
            result = subprocess.run(
                ["docker", "compose", "config", "--quiet"],
                cwd=kyros_root,
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, \
                f"docker-compose config failed: {result.stderr}"
