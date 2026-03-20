#!/usr/bin/env python3
"""
Generate docker-compose.yml from template and service definitions.

This script replaces generate-docker-compose.sh with a more maintainable
Python implementation that properly handles YAML merging.
"""

import os
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Installing PyYAML...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    import yaml


# Service name to env variable mapping
SERVICE_ENV_MAP = {
    "postgres": "INCLUDE_POSTGRES",
    "dagster": "INCLUDE_DAGSTER",
    "superset": "INCLUDE_SUPERSET",
    "dbt": "INCLUDE_DBT",
    "minio": "INCLUDE_MINIO",
    "jupyterlab": "INCLUDE_JUPYTERLAB",
    "trino": "INCLUDE_TRINO",
    "kafka": "INCLUDE_KAFKA",
    "flink": "INCLUDE_FLINK",
    "grafana": "INCLUDE_GRAFANA",
    "loki": "INCLUDE_LOKI",
    "promtail": "INCLUDE_PROMTAIL",
    "cloudbeaver": "INCLUDE_CLOUDBEAVER",
    "code-server": "INCLUDE_CODE_SERVER",
    "portainer": "INCLUDE_PORTAINER",
    "kyros": "INCLUDE_KYROS",
    "sqlpad": "INCLUDE_SQLPAD",
    "generator": "INCLUDE_GENERATOR",
    "keycloak": "INCLUDE_KEYCLOAK",
}


def load_env_file(env_path: Path) -> dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
    if not env_path.exists():
        print(f"Warning: {env_path} not found, using defaults")
        return env_vars

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

    return env_vars


def is_service_enabled(env_vars: dict[str, str], env_key: str) -> bool:
    """Check if a service is enabled based on environment variable."""
    return env_vars.get(env_key, "false").lower() == "true"


def load_service_yaml(services_dir: Path, service_name: str) -> dict[str, Any] | None:
    """Load a service YAML file and return its contents."""
    service_file = services_dir / f"{service_name}.yml"
    if not service_file.exists():
        print(f"Warning: Service file {service_file} not found")
        return None

    with open(service_file) as f:
        content = yaml.safe_load(f)

    return content


def generate_spark_worker(
    worker_num: int,
    env_vars: dict[str, str]
) -> dict[str, Any]:
    """Generate a Spark worker service definition."""
    return {
        "container_name": f"spark-worker-{worker_num}",
        "build": {
            "context": "./docker/spark-worker",
            "args": {
                "SPARK_BASE_IMAGE": "${IF_USING_LOCAL_REGISTRY}bitnami/spark:3.4.1"
            }
        },
        "ports": [
            f"808{worker_num}:808{worker_num}",
            f"404{worker_num}:404{worker_num}"
        ],
        "environment": [
            "SPARK_MODE=worker",
            f"SPARK_MASTER_HOST={env_vars.get('SPARK_MASTER_HOST', 'spark-master')}",
            f"SPARK_MASTER_PORT={env_vars.get('SPARK_MASTER_PORT', '7077')}",
            f"SPARK_WORKER_CORES={env_vars.get('SPARK_WORKER_CORES', '2')}",
            f"SPARK_WORKER_MEMORY={env_vars.get('SPARK_WORKER_MEMORY', '2G')}",
            f"SPARK_EXECUTOR_MEMORY={env_vars.get('SPARK_EXECUTOR_MEMORY', '2G')}",
            f"SPARK_EXECUTOR_CORES={env_vars.get('SPARK_EXECUTOR_CORES', '2')}",
            f"SPARK_UI_PORT=404{worker_num}"
        ],
        "volumes": [
            "data:/home/jovyan/data",
            "lab:/home/jovyan/lab"
        ],
        "depends_on": ["spark-master"],
        "networks": ["my-network"],
        "deploy": {
            "resources": {
                "limits": {
                    "memory": env_vars.get('SPARK_WORKER_MEMORY', '2G'),
                    "cpus": str(env_vars.get('SPARK_WORKER_CORES', '2'))
                }
            }
        }
    }


def build_base_compose(env_vars: dict[str, str], num_workers: int) -> dict[str, Any]:
    """Build the base docker-compose structure with core services."""
    # Worker dependencies for web service
    worker_deps = [f"spark-worker-{i}" for i in range(1, num_workers + 1)]

    compose = {
        "services": {
            "web": {
                "build": {
                    "context": "./docker/app",
                    "args": {"IMAGE": ""}
                },
                "container_name": "web",
                "ports": ["5002:5000"],
                "depends_on": ["spark-master"] + worker_deps,
                "networks": ["my-network"]
            },
            "spark-master": {
                "container_name": "spark-master",
                "build": {
                    "context": "./docker/spark-master",
                    "args": {
                        "IMAGE": "${IF_USING_LOCAL_REGISTRY}bitnami/spark:3.4.1"
                    }
                },
                "ports": [
                    "8080:8080",
                    "7077:7077",
                    "4040:4040"
                ],
                "environment": [
                    "SPARK_MASTER_HOST=spark-master",
                    "SPARK_MASTER_PORT=7077",
                    "SPARK_MASTER_WEBUI_PORT=8080",
                    "SPARK_UI_PORT=4040"
                ],
                "volumes": [
                    "data:/home/jovyan/data",
                    "lab:/home/jovyan/lab"
                ],
                "networks": ["my-network"],
                "healthcheck": {
                    "test": ["CMD-SHELL", "curl -f http://localhost:8080 || exit 1"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "30s"
                }
            },
            "hive-metastore": {
                "container_name": "hive-metastore",
                "build": {
                    "context": "./docker/hive-metastore",
                    "args": {
                        "IMAGE": "${IF_USING_LOCAL_REGISTRY}apache/hive:4.0.0"
                    }
                },
                "environment": [
                    "SERVICE_NAME=metastore",
                    "HIVE_METASTORE_USER=metastore_user",
                    "HIVE_METASTORE_PASSWORD=metastore_password",
                    "HIVE_METASTORE_DB_TYPE=postgres",
                    "HIVE_METASTORE_DB_HOST=postgres",
                    "HIVE_METASTORE_DB_PORT=5432",
                    "HIVE_METASTORE_DB_NAME=metastore",
                    "HIVE_METASTORE_DB_USER=metastore_user",
                    "HIVE_METASTORE_DB_PASSWORD=metastore_password"
                ],
                "ports": ["9083:9083"],
                "depends_on": ["postgres"],
                "networks": ["my-network"]
            },
            "spark-thrift-server": {
                "container_name": "spark-thrift-server",
                "build": {
                    "context": "./docker/spark-thrift-server",
                    "args": {
                        "IMAGE": "${IF_USING_LOCAL_REGISTRY}bitnami/spark:3.4.1",
                        "BASE_URL_JARS": "${BASE_URL_JARS}"
                    }
                },
                "environment": [
                    "SPARK_MASTER_HOST=spark-master",
                    "SPARK_MASTER_PORT=7077",
                    "SPARK_HOME=/opt/bitnami/spark"
                ],
                "depends_on": [
                    "postgres",
                    "spark-master",
                    "spark-worker-1",
                    "hive-metastore"
                ],
                "ports": ["10000:10000"],
                "networks": ["my-network"]
            }
        },
        "volumes": {
            "data": {
                "driver": "local",
                "driver_opts": {
                    "type": "none",
                    "o": "bind",
                    "device": "${PWD}/data/data"
                }
            },
            "lab": {
                "driver": "local",
                "driver_opts": {
                    "type": "none",
                    "o": "bind",
                    "device": "${PWD}/data/lab"
                }
            },
            "dagster-project": {
                "driver": "local",
                "driver_opts": {
                    "type": "none",
                    "o": "bind",
                    "device": f"${{PWD}}/data/orchestrate/dagster/{env_vars.get('DAGSTER_WORKSPACE', 'kyros')}"
                }
            },
            "transform": {
                "driver": "local",
                "driver_opts": {
                    "type": "none",
                    "o": "bind",
                    "device": "${PWD}/data/transform"
                }
            },
            "minio-data": {"driver": "local"},
            "cloudbeaver_data": {"driver": "local"},
            "grafana-data": {"driver": "local"},
            "loki-data": {"driver": "local"},
            "postgres-data": {"driver": "local"}
        },
        "networks": {
            "my-network": {"driver": "bridge"}
        }
    }

    return compose


def add_optional_services(
    compose: dict[str, Any],
    env_vars: dict[str, str],
    services_dir: Path
) -> None:
    """Add optional services based on environment configuration."""
    for service_name, env_key in SERVICE_ENV_MAP.items():
        if is_service_enabled(env_vars, env_key):
            service_data = load_service_yaml(services_dir, service_name)
            if service_data:
                # Merge service definitions
                for svc_name, svc_config in service_data.items():
                    compose["services"][svc_name] = svc_config


def add_spark_workers(
    compose: dict[str, Any],
    env_vars: dict[str, str],
    num_workers: int
) -> None:
    """Add Spark worker services."""
    for i in range(1, num_workers + 1):
        compose["services"][f"spark-worker-{i}"] = generate_spark_worker(i, env_vars)


def generate_docker_compose(
    base_dir: Path,
    env_vars: dict[str, str] | None = None,
    output_path: Path | None = None
) -> Path:
    """
    Generate docker-compose.yml from configuration.

    Args:
        base_dir: Root directory of the Kyros project
        env_vars: Environment variables (loaded from .env if not provided)
        output_path: Output file path (defaults to docker-compose.yml)

    Returns:
        Path to the generated docker-compose.yml
    """
    services_dir = base_dir / "services"

    # Load environment variables if not provided
    if env_vars is None:
        env_vars = load_env_file(base_dir / ".env")

    # Get number of workers
    num_workers = int(env_vars.get("WORKERS", "0"))

    # Build base compose structure
    compose = build_base_compose(env_vars, num_workers)

    # Add Spark workers
    if num_workers > 0:
        add_spark_workers(compose, env_vars, num_workers)

    # Add optional services
    add_optional_services(compose, env_vars, services_dir)

    # Write output
    if output_path is None:
        output_path = base_dir / "docker-compose.yml"

    with open(output_path, "w") as f:
        f.write("# Generated by Kyros - do not edit manually\n")
        f.write("# Regenerate with: python generate_compose.py\n\n")
        yaml.dump(compose, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Count enabled services
    enabled_count = sum(
        1 for env_key in SERVICE_ENV_MAP.values()
        if is_service_enabled(env_vars, env_key)
    )

    print(f"Generated {output_path} with {num_workers} Spark workers and {enabled_count} optional services.")

    return output_path


def main():
    """CLI entry point."""
    base_dir = Path(__file__).parent
    generate_docker_compose(base_dir)


if __name__ == "__main__":
    main()
