#!/bin/bash

# Get the caller's current directory
SCRIPT_DIR="$(pwd)"

# Load environment variables from the .env file located in the same directory as the script
export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)

# Initialize variables for additional services and worker services
additional_services=""
spark_worker_services=""
spark_worker_dependencies=""

# Include additional services based on environment variables
if [ "$INCLUDE_JUPYTERLAB" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/jupyterlab.yml")
 
"
fi

if [ "$INCLUDE_MKDOCS" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/mkdocs.yml")
 
"
fi

if [ "$INCLUDE_CODESERVER" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/code-server.yml")
 
"
fi

if [ "$INCLUDE_KAFKA" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/kafka.yml")
 
"
fi

if [ "$INCLUDE_PORTAINER" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/portainer.yml")
 
"
fi

if [ "$INCLUDE_TRINO" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/trino.yml")
 
"
fi

if [ "$INCLUDE_CLOUDBEAVER" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/cloudbeaver.yml")
 
"
fi

if [ "$INCLUDE_SQLPAD" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/sqlpad.yml")
 
"
fi

if [ "$INCLUDE_KYROS" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/kyros.yml")
 
"
fi

if [ "$INCLUDE_DAGSTER" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/dagster.yml")
 
"
fi

if [ "$INCLUDE_DBT" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/dbt.yml")
 
"
fi

if [ "$INCLUDE_FLINK" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/flink.yml")
 
"
fi

if [ "$INCLUDE_GRAFANA" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/grafana.yml")
 
"
fi

if [ "$INCLUDE_MINIO" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/minio.yml")
 
"
fi

if [ "$INCLUDE_CODE_SERVER" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/code-server.yml")
 
"
fi

if [ "$INCLUDE_GENERATOR" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/generator.yml")
 
"
fi

if [ "$INCLUDE_POSTGRES" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/postgres.yml")
 
"
fi

if [ "$INCLUDE_SUPERSET" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/superset.yml")
 
"
fi

if [ "$INCLUDE_OPENLDAP" = "true" ]; then
  additional_services+="$(cat "$SCRIPT_DIR/services/openldap.yml")
 
"
fi

if [ "$INCLUDE_SPARKS" = "true" ]; then
  spark_worker_services+="$(cat "$SCRIPT_DIR/services/spark.yml")\n"

  # Generate worker services
  for i in $(seq 1 $WORKERS); do
    spark_worker_services+="  spark-worker-$i:\n"
    spark_worker_services+="    container_name: spark-worker-$i\n"
    spark_worker_services+="    build:\n"
    spark_worker_services+="      context: ./docker/spark-worker\n"
    spark_worker_services+="      args:\n"
    spark_worker_services+="        SPARK_BASE_IMAGE: \${IF_USING_LOCAL_REGISTRY}bitnami/spark:3.4.1\n"
    spark_worker_services+="    ports:\n"
    spark_worker_services+="      - 808$i:808$i  # Spark Worker $i Web UI\n"
    spark_worker_services+="      - 404$i:404$i  # Spark Worker $i UI Port\n"
    spark_worker_services+="    environment:\n"
    spark_worker_services+="      - SPARK_MODE=worker\n"
    spark_worker_services+="      - SPARK_MASTER_HOST=$SPARK_MASTER_HOST\n"
    spark_worker_services+="      - SPARK_MASTER_PORT=$SPARK_MASTER_PORT\n"
    spark_worker_services+="      - SPARK_WORKER_CORES=${SPARK_WORKER_CORES}\n"
    spark_worker_services+="      - SPARK_WORKER_MEMORY=${SPARK_WORKER_MEMORY}\n"
    spark_worker_services+="      - SPARK_EXECUTOR_MEMORY=${SPARK_EXECUTOR_MEMORY}\n"
    spark_worker_services+="      - SPARK_EXECUTOR_CORES=${SPARK_EXECUTOR_CORES}\n"
    spark_worker_services+="      - SPARK_UI_PORT=404$i\n"
    spark_worker_services+="    volumes:\n"
    spark_worker_services+="      - data:/home/jovyan/data\n"
    spark_worker_services+="      - lab:/home/jovyan/lab\n"
    spark_worker_services+="    depends_on:\n"
    spark_worker_services+="      - spark-master\n"
    spark_worker_services+="    networks:\n"
    spark_worker_services+="      - my-network\n\n"
    spark_worker_dependencies+="      - spark-worker-$i\n"
  done

  # Now, handle the multiline content using the here document
  sed -e "/{{ADDITIONAL_SERVICES}}/r /dev/stdin" -e "//d" "$SCRIPT_DIR/docker-compose.template.yml" > "$SCRIPT_DIR/docker-compose.yml" <<EOF
$additional_services
EOF

else
  # If Spark is not included, handle only additional services
  sed -e "/{{ADDITIONAL_SERVICES}}/r /dev/stdin" -e "//d" "$SCRIPT_DIR/docker-compose.template.yml" > "$SCRIPT_DIR/docker-compose.yml" <<EOF
$additional_services
EOF

fi



echo "docker-compose.yml generated."
