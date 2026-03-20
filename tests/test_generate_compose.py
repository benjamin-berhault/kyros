"""Tests for generate_compose module."""

import pytest
from pathlib import Path
import tempfile
import yaml

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_compose import (
    load_env_file,
    is_service_enabled,
    generate_spark_worker,
    build_base_compose,
    generate_docker_compose,
    SERVICE_ENV_MAP,
)


class TestLoadEnvFile:
    """Tests for load_env_file function."""

    def test_load_valid_env_file(self, tmp_path):
        """Test loading a valid .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
# Comment line
INCLUDE_POSTGRES=true
INCLUDE_KAFKA=false
WORKERS=2
SPARK_WORKER_MEMORY=4G
""")
        result = load_env_file(env_file)

        assert result["INCLUDE_POSTGRES"] == "true"
        assert result["INCLUDE_KAFKA"] == "false"
        assert result["WORKERS"] == "2"
        assert result["SPARK_WORKER_MEMORY"] == "4G"

    def test_load_missing_env_file(self, tmp_path):
        """Test loading a non-existent .env file returns empty dict."""
        result = load_env_file(tmp_path / "nonexistent.env")
        assert result == {}

    def test_skip_comment_lines(self, tmp_path):
        """Test that comment lines are skipped."""
        env_file = tmp_path / ".env"
        env_file.write_text("# This is a comment\nVALID_KEY=value")
        result = load_env_file(env_file)

        assert "# This is a comment" not in result
        assert result["VALID_KEY"] == "value"


class TestIsServiceEnabled:
    """Tests for is_service_enabled function."""

    def test_service_enabled_true(self):
        """Test service is enabled when value is 'true'."""
        env_vars = {"INCLUDE_POSTGRES": "true"}
        assert is_service_enabled(env_vars, "INCLUDE_POSTGRES") is True

    def test_service_enabled_false(self):
        """Test service is disabled when value is 'false'."""
        env_vars = {"INCLUDE_POSTGRES": "false"}
        assert is_service_enabled(env_vars, "INCLUDE_POSTGRES") is False

    def test_service_missing_defaults_false(self):
        """Test missing service defaults to disabled."""
        env_vars = {}
        assert is_service_enabled(env_vars, "INCLUDE_POSTGRES") is False

    def test_service_case_insensitive(self):
        """Test that value comparison is case insensitive."""
        env_vars = {"INCLUDE_POSTGRES": "TRUE"}
        assert is_service_enabled(env_vars, "INCLUDE_POSTGRES") is True


class TestGenerateSparkWorker:
    """Tests for generate_spark_worker function."""

    def test_generates_correct_structure(self):
        """Test spark worker has correct structure."""
        env_vars = {
            "SPARK_MASTER_HOST": "spark-master",
            "SPARK_MASTER_PORT": "7077",
            "SPARK_WORKER_CORES": "4",
            "SPARK_WORKER_MEMORY": "8G",
        }

        worker = generate_spark_worker(1, env_vars)

        assert worker["container_name"] == "spark-worker-1"
        assert "808" in worker["ports"][0]
        assert worker["depends_on"] == ["spark-master"]
        assert "my-network" in worker["networks"]

    def test_unique_ports_per_worker(self):
        """Test each worker gets unique ports."""
        env_vars = {}

        worker1 = generate_spark_worker(1, env_vars)
        worker2 = generate_spark_worker(2, env_vars)

        assert worker1["ports"][0] != worker2["ports"][0]
        assert worker1["container_name"] != worker2["container_name"]


class TestBuildBaseCompose:
    """Tests for build_base_compose function."""

    def test_includes_required_services(self):
        """Test base compose includes web, spark-master, etc."""
        compose = build_base_compose({}, 0)

        assert "web" in compose["services"]
        assert "spark-master" in compose["services"]
        assert "hive-metastore" in compose["services"]

    def test_includes_volumes(self):
        """Test base compose includes required volumes."""
        compose = build_base_compose({}, 0)

        assert "data" in compose["volumes"]
        assert "lab" in compose["volumes"]
        assert "dagster-project" in compose["volumes"]

    def test_includes_network(self):
        """Test base compose includes network definition."""
        compose = build_base_compose({}, 0)

        assert "my-network" in compose["networks"]

    def test_worker_dependencies_added(self):
        """Test web service depends on workers."""
        compose = build_base_compose({}, 2)

        deps = compose["services"]["web"]["depends_on"]
        assert "spark-worker-1" in deps
        assert "spark-worker-2" in deps


class TestGenerateDockerCompose:
    """Tests for generate_docker_compose function."""

    def test_generates_valid_yaml(self, tmp_path):
        """Test generated file is valid YAML."""
        # Create minimal services directory
        services_dir = tmp_path / "services"
        services_dir.mkdir()

        # Create a test service file
        postgres_yml = services_dir / "postgres.yml"
        postgres_yml.write_text("""
postgres:
  image: postgres:15
  ports:
    - "5432:5432"
""")

        env_vars = {"INCLUDE_POSTGRES": "true", "WORKERS": "0"}
        output = tmp_path / "docker-compose.yml"

        generate_docker_compose(tmp_path, env_vars, output)

        # Verify file exists and is valid YAML
        assert output.exists()
        with open(output) as f:
            content = f.read()
            # Skip comment lines
            yaml_content = "\n".join(
                line for line in content.split("\n")
                if not line.startswith("#")
            )
            parsed = yaml.safe_load(yaml_content)

        assert "services" in parsed
        assert "volumes" in parsed
        assert "networks" in parsed

    def test_includes_enabled_services(self, tmp_path):
        """Test enabled services are included."""
        services_dir = tmp_path / "services"
        services_dir.mkdir()

        postgres_yml = services_dir / "postgres.yml"
        postgres_yml.write_text("""
postgres:
  image: postgres:15
  container_name: postgres
""")

        env_vars = {"INCLUDE_POSTGRES": "true", "WORKERS": "0"}
        output = tmp_path / "docker-compose.yml"

        generate_docker_compose(tmp_path, env_vars, output)

        with open(output) as f:
            content = f.read()
            yaml_content = "\n".join(
                line for line in content.split("\n")
                if not line.startswith("#")
            )
            parsed = yaml.safe_load(yaml_content)

        assert "postgres" in parsed["services"]

    def test_excludes_disabled_services(self, tmp_path):
        """Test disabled services are not included."""
        services_dir = tmp_path / "services"
        services_dir.mkdir()

        kafka_yml = services_dir / "kafka.yml"
        kafka_yml.write_text("""
kafka:
  image: confluentinc/cp-kafka:7.5.0
""")

        env_vars = {"INCLUDE_KAFKA": "false", "WORKERS": "0"}
        output = tmp_path / "docker-compose.yml"

        generate_docker_compose(tmp_path, env_vars, output)

        with open(output) as f:
            content = f.read()
            yaml_content = "\n".join(
                line for line in content.split("\n")
                if not line.startswith("#")
            )
            parsed = yaml.safe_load(yaml_content)

        assert "kafka" not in parsed["services"]

    def test_generates_spark_workers(self, tmp_path):
        """Test spark workers are generated when WORKERS > 0."""
        services_dir = tmp_path / "services"
        services_dir.mkdir()

        env_vars = {"WORKERS": "2"}
        output = tmp_path / "docker-compose.yml"

        generate_docker_compose(tmp_path, env_vars, output)

        with open(output) as f:
            content = f.read()
            yaml_content = "\n".join(
                line for line in content.split("\n")
                if not line.startswith("#")
            )
            parsed = yaml.safe_load(yaml_content)

        assert "spark-worker-1" in parsed["services"]
        assert "spark-worker-2" in parsed["services"]


class TestServiceEnvMap:
    """Tests for SERVICE_ENV_MAP constant."""

    def test_all_services_have_mapping(self):
        """Test all expected services are in the map."""
        expected_services = [
            "postgres", "dagster", "superset", "dbt", "minio",
            "jupyterlab", "trino", "kafka", "flink", "grafana",
            "loki", "promtail", "cloudbeaver", "portainer", "kyros"
        ]

        for service in expected_services:
            assert service in SERVICE_ENV_MAP, f"Missing service: {service}"

    def test_env_vars_follow_convention(self):
        """Test all env vars follow INCLUDE_* naming convention."""
        for service, env_var in SERVICE_ENV_MAP.items():
            assert env_var.startswith("INCLUDE_"), \
                f"Env var {env_var} for {service} doesn't follow INCLUDE_* convention"
