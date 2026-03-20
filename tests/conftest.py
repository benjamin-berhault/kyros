"""
Pytest configuration and fixtures for Kyros tests.
"""
import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
KYROS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(KYROS_ROOT))


@pytest.fixture
def kyros_root():
    """Return the Kyros project root directory."""
    return KYROS_ROOT


@pytest.fixture
def services_dir(kyros_root):
    """Return the services directory."""
    return kyros_root / "services"


@pytest.fixture
def presets_dir(kyros_root):
    """Return the presets directory."""
    return kyros_root / "presets"


@pytest.fixture
def docker_dir(kyros_root):
    """Return the docker directory."""
    return kyros_root / "docker"


@pytest.fixture
def all_service_files(services_dir):
    """Return all service YAML files."""
    return list(services_dir.glob("*.yml"))


@pytest.fixture
def all_preset_files(presets_dir):
    """Return all preset .env files."""
    return list(presets_dir.glob("level-*.env"))


@pytest.fixture
def sample_env_content():
    """Return sample .env content for testing."""
    return """
INCLUDE_POSTGRES=true
INCLUDE_DAGSTER=true
INCLUDE_SUPERSET=false
INCLUDE_DBT=true
WORKERS=2
POSTGRES_USER=test
POSTGRES_PASSWORD=test123
"""
