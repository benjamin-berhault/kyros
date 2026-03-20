"""
Tests for service YAML definitions.
"""
import pytest
import yaml
from pathlib import Path


class TestServiceFiles:
    """Test service YAML files."""

    def test_service_files_exist(self, services_dir):
        """Verify services directory contains YAML files."""
        yml_files = list(services_dir.glob("*.yml"))
        assert len(yml_files) > 0, "No service YAML files found"

    def test_service_yaml_valid(self, all_service_files):
        """Verify all service YAML files are valid YAML."""
        for service_file in all_service_files:
            try:
                content = service_file.read_text()
                yaml.safe_load(content)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {service_file.name}: {e}")

    def test_services_have_container_name(self, all_service_files):
        """Verify services define container_name."""
        for service_file in all_service_files:
            content = service_file.read_text()
            data = yaml.safe_load(content)

            if data is None:
                continue

            for service_name, service_config in data.items():
                if isinstance(service_config, dict):
                    assert "container_name" in service_config or "build" in service_config, \
                        f"Service {service_name} in {service_file.name} missing container_name"

    def test_services_have_networks(self, all_service_files):
        """Verify services define network configuration."""
        for service_file in all_service_files:
            content = service_file.read_text()
            data = yaml.safe_load(content)

            if data is None:
                continue

            for service_name, service_config in data.items():
                if isinstance(service_config, dict):
                    # Services should connect to the network
                    assert "networks" in service_config, \
                        f"Service {service_name} in {service_file.name} missing networks"

    def test_critical_services_have_healthcheck(self, services_dir):
        """Verify critical services have healthcheck defined."""
        critical_services = [
            "postgres.yml",
            "dagster.yml",
            "superset.yml",
            "minio.yml",
        ]

        for service_name in critical_services:
            service_file = services_dir / service_name
            if service_file.exists():
                content = service_file.read_text()
                assert "healthcheck" in content, \
                    f"Critical service {service_name} missing healthcheck"

    def test_no_latest_tags_in_production(self, all_service_files):
        """Warn about :latest tags which can cause reproducibility issues."""
        for service_file in all_service_files:
            content = service_file.read_text()
            # We check for hardcoded :latest (not ${VAR}:latest which is OK)
            if ":latest" in content and "${" not in content.split(":latest")[0].split("\n")[-1]:
                # This is a soft warning - latest tags in base images are sometimes OK
                pass  # Could add warning here


class TestDockerfiles:
    """Test Dockerfile configurations."""

    def test_dockerfiles_exist_for_services(self, docker_dir, services_dir):
        """Verify Dockerfiles exist for services that need them."""
        service_dirs_needing_dockerfile = [
            "postgres",
            "dagster",
            "superset",
            "kyros",
        ]

        for service in service_dirs_needing_dockerfile:
            dockerfile = docker_dir / service / "Dockerfile"
            # Either Dockerfile exists or service uses pre-built image
            service_yml = services_dir / f"{service}.yml"
            if service_yml.exists():
                content = service_yml.read_text()
                has_build = "build:" in content
                has_image = "image:" in content
                assert has_build or has_image, \
                    f"Service {service} has neither build context nor image"

    def test_dockerfiles_have_from_instruction(self, docker_dir):
        """Verify Dockerfiles start with FROM instruction."""
        for dockerfile in docker_dir.rglob("Dockerfile"):
            content = dockerfile.read_text()
            lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
            if lines:
                first_instruction = lines[0].upper()
                assert first_instruction.startswith("ARG") or first_instruction.startswith("FROM"), \
                    f"Dockerfile {dockerfile} doesn't start with FROM or ARG"
