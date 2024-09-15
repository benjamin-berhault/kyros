#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Initialize variables for additional services and worker services
additional_services=""
spark_worker_services=""
spark_worker_dependencies=""

# Include additional services based on environment variables
if [ "$INCLUDE_JUPYTERLAB" = "true" ]; then
  additional_services+="$(cat services/jupyterlab.yml)
 
"
fi

if [ "$INCLUDE_KAFKA" = "true" ]; then
  additional_services+="$(cat services/kafka.yml)

"
fi

# Include additional services based on environment variables
if [ "$INCLUDE_PORTAINER" = "true" ]; then
  additional_services+="$(cat services/portainer.yml)
 
"
fi

# Include additional services based on environment variables
if [ "$INCLUDE_TRINO" = "true" ]; then
  additional_services+="$(cat services/trino.yml)
 
"
fi

# Include additional services based on environment variables
if [ "$INCLUDE_CLOUDBEAVER" = "true" ]; then
  additional_services+="$(cat services/cloudbeaver.yml)
 
"
fi

# Include additional services based on environment variables
if [ "$INCLUDE_KYROS" = "true" ]; then
  additional_services+="$(cat services/kyros.yml)
 
"
fi

# Include additional services based on environment variables
if [ "$INCLUDE_DAGSTER" = "true" ]; then
  additional_services+="$(cat services/dagster.yml)
 
"
fi

# Include additional services based on environment variables
if [ "$INCLUDE_DBT" = "true" ]; then
  additional_services+="$(cat services/dbt.yml)
 
"
fi

# Include additional services based on environment variables
if [ "$INCLUDE_FLINK" = "true" ]; then
  additional_services+="$(cat services/flink.yml)
 
"
fi

# Include additional services based on environment variables
if [ "$INCLUDE_GRAFANA" = "true" ]; then
  additional_services+="$(cat services/grafana.yml)
 
"
fi


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
  spark_worker_services+="      - ./shared-workspace:/home/jovyan/work\n"
  spark_worker_services+="      - ./data/delta_lake:/home/jovyan/delta_lake\n"
  spark_worker_services+="      - ./data/parquet:/home/jovyan/parquet\n"
  spark_worker_services+="      - ./data/iceberg:/home/jovyan/iceberg\n"
  spark_worker_services+="    depends_on:\n"
  spark_worker_services+="      - spark-master\n"
  spark_worker_services+="    networks:\n"
  spark_worker_services+="      - my-network\n\n"
  spark_worker_dependencies+="      - spark-worker-$i\n"
done

# # Replace placeholders in the template with generated services
# sed -e "s|{{SPARK_WORKER_SERVICES}}|$spark_worker_services|" \
#     -e "s|{{ADDITIONAL_SERVICES}}|$additional_services|" \
#     docker-compose.template.yml > docker-compose.yml

# First, perform the single-line substitutions
sed -e "s|{{SPARK_WORKER_SERVICES}}|$spark_worker_services|" \
    -e "s|{{SPARK_WORKER_DEPENDENCIES}}|$spark_worker_dependencies|" \
    docker-compose.template.yml > docker-compose.tmp.yml

# Now, handle the multiline content using the here document
sed -e "/{{ADDITIONAL_SERVICES}}/r /dev/stdin" -e "//d" docker-compose.tmp.yml > docker-compose.yml <<EOF
$additional_services
EOF

# Clean up the temporary file
rm docker-compose.tmp.yml

echo "Generated docker-compose.yml with $WORKERS Spark workers and optional services."
