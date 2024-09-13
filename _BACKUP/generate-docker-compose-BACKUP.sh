#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Initialize variables for workers and additional services
spark_worker_services=""
spark_worker_dependencies=""
additional_services=""
zeppelin_volume=""

# Conditionally include JupyterLab
if [ "$INCLUDE_JUPYTERLAB" = "true" ]; then
  additional_services+="  jupyterlab:\n"
  additional_services+="    container_name: jupyterlab\n"
  additional_services+="    build:\n"
  additional_services+="      context: ./docker/jupyterlab\n"
  additional_services+="      args:\n"
  additional_services+="        BASE_IMAGE: jupyter/base-notebook:latest\n"
  additional_services+="        spark_version: 3.4.1\n"
  additional_services+="        jupyterlab_version: 4.2.4\n"
  additional_services+="        sparksql_magic_version: 0.0.3\n"
  additional_services+="        kafka_python_version: 2.0.2\n"
  additional_services+="    environment:\n"
  additional_services+="      - JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64\n"
  additional_services+="    ports:\n"
  additional_services+="      - 8888:8888\n"
  additional_services+="      - 4045:4040\n"
  additional_services+="    volumes:\n"
  additional_services+="      - ./shared-workspace:/home/jovyan/work\n"
  additional_services+="      - ./data/delta_lake:/home/jovyan/delta_lake\n"
  additional_services+="    depends_on:\n"
  additional_services+="      - spark-master\n"
  additional_services+="    networks:\n"
  additional_services+="      - my-network\n\n"
fi

# Conditionally include Zeppelin
if [ "$INCLUDE_ZEPPELIN" = "true" ]; then
  additional_services+="  zeppelin:\n"
  additional_services+="    image: apache/zeppelin:0.10.0\n"
  additional_services+="    container_name: zeppelin\n"
  additional_services+="    ports:\n"
  additional_services+="      - 9001:8080\n"
  additional_services+="    environment:\n"
  additional_services+="      - ZEPPELIN_NOTEBOOK_DIR=/notebook\n"
  additional_services+="      - SPARK_HOME=/spark\n"
  additional_services+="    volumes:\n"
  additional_services+="      - ./data/zeppelin-data:/notebook\n"
  additional_services+="    depends_on:\n"
  additional_services+="      - spark-master\n"
  additional_services+="    networks:\n"
  additional_services+="      - my-network\n\n"

  # Prepare the zeppelin-data volume
  # zeppelin_volume+="  zeppelin-data:\n"
  # zeppelin_volume+="    driver: local\n"
  # zeppelin_volume+="    driver_opts:\n"
  # zeppelin_volume+="      type: none\n"
  # zeppelin_volume+="      o: bind\n"
  # zeppelin_volume+="      device: ${PWD}/zeppelin-data\n"
fi

# Conditionally include Kafka
if [ "$INCLUDE_KAFKA" = "true" ]; then
  additional_services+="  kafka:\n"
  additional_services+="    container_name: kafka\n"
  additional_services+="    image: docker.io/bitnami/kafka:3.5.1\n"
  additional_services+="    ports:\n"
  additional_services+="      - 9092:9092\n"
  additional_services+="      - 29092:29092\n"
  additional_services+="    environment:\n"
  additional_services+="      - BITNAMI_DEBUG=yes\n"
  additional_services+="      - KAFKA_ENABLE_KRAFT=true\n"
  additional_services+="      - KAFKA_CFG_NODE_ID=1\n"
  additional_services+="      - KAFKA_CFG_PROCESS_ROLES=broker,controller\n"
  additional_services+="      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka:29092\n"
  additional_services+="      - KAFKA_CFG_LISTENERS=PLAINTEXT://kafka:9092,CONTROLLER://kafka:29092\n"
  additional_services+="      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092\n"
  additional_services+="      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT\n"
  additional_services+="      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER\n"
  additional_services+="      - KAFKA_CFG_INTER_BROKER_LISTENER_NAME=PLAINTEXT\n"
  additional_services+="      - ALLOW_PLAINTEXT_LISTENER=yes\n\n"
fi

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
  spark_worker_services+="    depends_on:\n"
  spark_worker_services+="      - spark-master\n"
  spark_worker_services+="    networks:\n"
  spark_worker_services+="      - my-network\n\n"
  spark_worker_dependencies+="      - spark-worker-$i\n"
done

# Replace placeholders in template with generated services
sed -e "s|{{SPARK_WORKER_SERVICES}}|$spark_worker_services|" \
    -e "s|{{SPARK_WORKER_DEPENDENCIES}}|$spark_worker_dependencies|" \
    -e "s|{{ADDITIONAL_SERVICES}}|$additional_services|" \
    docker-compose.template.yml > docker-compose.yml
    #-e "s|# ZEPPELIN_VOLUME_PLACEHOLDER|volumes:\n$zeppelin_volume|" \

echo "Generated docker-compose.yml with $WORKERS Spark workers and optional services."
