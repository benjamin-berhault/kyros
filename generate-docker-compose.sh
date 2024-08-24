#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Initialize variables for workers
spark_worker_services=""
spark_worker_dependencies=""

# Generate worker services
for i in $(seq 1 $WORKERS); do
  spark_worker_services+="  spark-worker-$i:\n"
  spark_worker_services+="    container_name: spark-worker-$i\n"
  spark_worker_services+="    build:\n"
  spark_worker_services+="      context: ./docker/spark-worker\n"
  spark_worker_services+="      args:\n"
  spark_worker_services+="        SPARK_BASE_IMAGE: bitnami/spark:3.4.1\n"
  spark_worker_services+="    ports:\n"
  spark_worker_services+="      - 808$i:808$i  # Spark Worker $i Web UI\n"
  spark_worker_services+="      - 404$i:404$i  # Spark Worker $i UI Port\n"
  spark_worker_services+="    environment:\n"
  spark_worker_services+="      - SPARK_MODE=worker\n"
  spark_worker_services+="      - SPARK_MASTER_HOST=spark-master\n"
  spark_worker_services+="      - SPARK_MASTER_PORT=7077\n"
  spark_worker_services+="      - SPARK_WORKER_CORES=${SPARK_WORKER_CORES}\n"
  spark_worker_services+="      - SPARK_WORKER_MEMORY=${SPARK_WORKER_MEMORY}\n"
  spark_worker_services+="      - SPARK_EXECUTOR_MEMORY=${SPARK_EXECUTOR_MEMORY}\n"
  spark_worker_services+="      - SPARK_EXECUTOR_CORES=${SPARK_EXECUTOR_CORES}\n"
  spark_worker_services+="      - SPARK_UI_PORT=404$i\n"
  spark_worker_services+="    volumes:\n"
  spark_worker_services+="      - shared-workspace:/home/jovyan/work\n"
  spark_worker_services+="      - delta_lake:/home/jovyan/delta_lake\n"
  spark_worker_services+="    depends_on:\n"
  spark_worker_services+="      - spark-master\n"
  spark_worker_services+="    networks:\n"
  spark_worker_services+="      - my-network\n\n"
  spark_worker_dependencies+="      - spark-worker-$i\n"
done

# Replace placeholders in template with generated services
sed -e "s|{{SPARK_WORKER_SERVICES}}|$spark_worker_services|" \
    -e "s|{{SPARK_WORKER_DEPENDENCIES}}|$spark_worker_dependencies|" \
    docker-compose.template.yml > docker-compose.yml

echo "Generated docker-compose.yml with $WORKERS Spark workers."
