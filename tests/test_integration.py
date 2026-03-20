"""
Integration tests for Kyros platform services.

These tests verify:
- Service health endpoints
- Container startup
- Inter-service connectivity

Requirements:
- Services must be running (make up)
- Tests are skipped if services aren't available

Run with: pytest tests/test_integration.py -v
"""

import os
import subprocess
import time
from urllib.error import URLError
from urllib.request import urlopen, Request

import pytest


def is_docker_running() -> bool:
    """Check if Docker is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_service_running(container_name: str) -> bool:
    """Check if a specific container is running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name=^{container_name}$", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return container_name in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_url(url: str, timeout: int = 5, expected_status: int = 200) -> bool:
    """Check if a URL responds with expected status."""
    try:
        request = Request(url, headers={"User-Agent": "Kyros-Test"})
        response = urlopen(request, timeout=timeout)
        return response.status == expected_status
    except (URLError, TimeoutError):
        return False


def wait_for_service(url: str, max_wait: int = 30, interval: int = 2) -> bool:
    """Wait for a service to become available."""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if check_url(url):
            return True
        time.sleep(interval)
    return False


# Skip all tests if Docker isn't running
pytestmark = pytest.mark.skipif(
    not is_docker_running(),
    reason="Docker is not running"
)


class TestServiceHealth:
    """Test service health endpoints."""

    @pytest.mark.skipif(
        not is_service_running("postgres"),
        reason="PostgreSQL not running"
    )
    def test_postgres_health(self):
        """Test PostgreSQL is accepting connections."""
        result = subprocess.run(
            ["docker", "exec", "postgres", "pg_isready", "-U", "kyros"],
            capture_output=True,
            timeout=10
        )
        assert result.returncode == 0, "PostgreSQL is not accepting connections"

    @pytest.mark.skipif(
        not is_service_running("dagster"),
        reason="Dagster not running"
    )
    def test_dagster_health(self):
        """Test Dagster health endpoint."""
        assert check_url("http://localhost:3000/server_info"), \
            "Dagster health check failed"

    @pytest.mark.skipif(
        not is_service_running("superset"),
        reason="Superset not running"
    )
    def test_superset_health(self):
        """Test Superset health endpoint."""
        assert check_url("http://localhost:8088/health"), \
            "Superset health check failed"

    @pytest.mark.skipif(
        not is_service_running("grafana"),
        reason="Grafana not running"
    )
    def test_grafana_health(self):
        """Test Grafana health endpoint."""
        assert check_url("http://localhost:3002/api/health"), \
            "Grafana health check failed"

    @pytest.mark.skipif(
        not is_service_running("minio"),
        reason="MinIO not running"
    )
    def test_minio_health(self):
        """Test MinIO health endpoint."""
        assert check_url("http://localhost:9000/minio/health/live"), \
            "MinIO health check failed"

    @pytest.mark.skipif(
        not is_service_running("loki"),
        reason="Loki not running"
    )
    def test_loki_health(self):
        """Test Loki readiness endpoint."""
        assert check_url("http://localhost:3100/ready"), \
            "Loki health check failed"

    @pytest.mark.skipif(
        not is_service_running("kyros"),
        reason="Kyros dashboard not running"
    )
    def test_kyros_health(self):
        """Test Kyros dashboard health endpoint."""
        assert check_url("http://localhost:5000/health"), \
            "Kyros dashboard health check failed"


class TestServiceConnectivity:
    """Test connectivity between services."""

    @pytest.mark.skipif(
        not is_service_running("dagster") or not is_service_running("postgres"),
        reason="Dagster or PostgreSQL not running"
    )
    def test_dagster_postgres_connection(self):
        """Test Dagster can connect to PostgreSQL."""
        result = subprocess.run(
            ["docker", "logs", "dagster", "--tail", "50"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert "connection refused" not in result.stdout.lower()
        assert "could not connect" not in result.stdout.lower()

    @pytest.mark.skipif(
        not is_service_running("superset") or not is_service_running("postgres"),
        reason="Superset or PostgreSQL not running"
    )
    def test_superset_postgres_connection(self):
        """Test Superset can connect to PostgreSQL."""
        result = subprocess.run(
            ["docker", "logs", "superset", "--tail", "50"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert "connection refused" not in result.stdout.lower()

    @pytest.mark.skipif(
        not is_service_running("grafana") or not is_service_running("loki"),
        reason="Grafana or Loki not running"
    )
    def test_grafana_loki_connection(self):
        """Test Grafana can connect to Loki datasource."""
        try:
            request = Request(
                "http://localhost:3002/api/datasources",
                headers={
                    "User-Agent": "Kyros-Test",
                    "Authorization": "Basic YWRtaW46YWRtaW4="
                }
            )
            response = urlopen(request, timeout=10)
            data = response.read().decode()
            assert "Loki" in data or "loki" in data
        except URLError:
            pytest.skip("Could not connect to Grafana API")


class TestContainerStatus:
    """Test container status and resources."""

    def test_no_restarting_containers(self):
        """Verify no containers are in a restart loop."""
        result = subprocess.run(
            ["docker", "ps", "--filter", "status=restarting", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        restarting = [c for c in result.stdout.strip().split("\n") if c]
        assert len(restarting) == 0, f"Containers restarting: {restarting}"

    def test_no_exited_containers(self):
        """Check for unexpectedly exited containers."""
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", "status=exited",
             "--filter", "label=com.docker.compose.project",
             "--format", "{{.Names}}: {{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        exited = result.stdout.strip()
        unexpected = [
            line for line in exited.split("\n")
            if line and "Exited (0)" not in line
        ]
        assert len(unexpected) == 0, f"Unexpectedly exited containers:\n{chr(10).join(unexpected)}"


class TestNetworkConnectivity:
    """Test Docker network connectivity."""

    def test_network_exists(self):
        """Verify the kyros network exists."""
        result = subprocess.run(
            ["docker", "network", "ls", "--filter", "name=my-network", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert "network" in result.stdout.lower() or "my-network" in result.stdout

    @pytest.mark.skipif(
        not is_service_running("postgres"),
        reason="PostgreSQL not running"
    )
    def test_dns_resolution(self):
        """Test DNS resolution within container network."""
        result = subprocess.run(
            ["docker", "exec", "postgres", "getent", "hosts", "postgres"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, "DNS resolution failed for postgres"


class TestDataPersistence:
    """Test data persistence and volumes."""

    @pytest.mark.skipif(
        not is_service_running("postgres"),
        reason="PostgreSQL not running"
    )
    def test_postgres_data_volume(self):
        """Test PostgreSQL data directory is properly mounted."""
        result = subprocess.run(
            ["docker", "exec", "postgres", "ls", "/var/lib/postgresql/data"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, "PostgreSQL data directory not accessible"

    @pytest.mark.skipif(
        not is_service_running("grafana"),
        reason="Grafana not running"
    )
    def test_grafana_data_volume(self):
        """Test Grafana data directory is properly mounted."""
        result = subprocess.run(
            ["docker", "exec", "grafana", "ls", "/var/lib/grafana"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, "Grafana data directory not accessible"


@pytest.fixture(scope="session")
def docker_compose_project():
    """Fixture to get docker-compose project info."""
    result = subprocess.run(
        ["docker", "compose", "ps", "--format", "json"],
        capture_output=True,
        text=True,
        timeout=10
    )
    return result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
