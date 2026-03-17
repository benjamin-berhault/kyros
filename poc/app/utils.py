import os
import subprocess

def generate_env_file(config):
    variables = [
        "BASE_URL_JARS", "INCLUDE_MKDOCS", "INCLUDE_JUPYTERLAB", "INCLUDE_JUPYTERLAB_CPP_SUPPORT",
        "INCLUDE_JUPYTERLAB_GO_SUPPORT", "INCLUDE_JUPYTERLAB_RUST_SUPPORT", "INCLUDE_JUPYTERLAB_DBT_SUPPORT",
        "INCLUDE_JUPYTERLAB_DBT_POSTGRES_SUPPORT", "INCLUDE_JUPYTERLAB_DBT_SPARK_SUPPORT", "INCLUDE_CLOUDBEAVER",
        "INCLUDE_SQLPAD", "INCLUDE_CODESERVER", "INCLUDE_KAFKA", "INCLUDE_MINIO", "INCLUDE_TRINO",
        "INCLUDE_DAGSTER", "INCLUDE_DBT", "INCLUDE_FLINK", "INCLUDE_GRAFANA", "INCLUDE_POSTGRES",
        "INCLUDE_SUPERSET", "INCLUDE_OPENLDAP", "INCLUDE_KEYCLOAK", "INCLUDE_SPARKS", "WORKERS"
    ]
    with open('.env', 'w') as f:
        for var in variables:
            value = config.get(var, 'false')  # Default to 'false' if not provided
            f.write(f"{var}={value}\n")

