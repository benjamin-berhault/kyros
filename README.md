# Data Engineering with Apache Spark and Delta Lake

This project provides a Docker-based environment for data engineering using Apache Spark and Delta Lake. The setup includes a JupyterLab instance preconfigured with Spark, Delta Lake, and other necessary tools.

## Architecture Overview

- **JupyterLab**: A browser-based interactive computing environment that enables you to work with documents and activities such as Jupyter notebooks, text editors, terminals, and custom components.
- **Apache Spark**: A powerful open-source distributed computing system that provides an interface for programming entire clusters with implicit data parallelism and fault tolerance.
- **Delta Lake**: An open-source storage layer that brings ACID transactions to Apache Spark and big data workloads.

## Prerequisites

- Docker and Docker Compose installed on your machine.
- Internet connection to pull Docker images and download dependencies.

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Configure Environment Variables

Create a `.env` file to define the characteristics of the architecture:

```bash
cp .env.example .env
```

Edit the `.env` file to configure your environment:

```bash
nano .env
```

### 3. Prepare Permissions and Generate Docker Compose File

Run the setup scripts:

```bash
./before_docker-compose.sh
./generate-docker-compose.sh
```

### 4. Build and Start the Docker Containers

You can choose between building without cache or simply bringing up the containers:

```bash
# Build Images Without Cache
docker compose -f docker-compose.yml build --no-cache

# Bring Up Containers
docker compose -f docker-compose.yml up --remove-orphans -d
```

### 5. Access JupyterLab

Once the containers are up, you can access JupyterLab at:

```
http://localhost:8888
```

## Common Commands

### Stop and Remove All Containers

```bash
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
```

### Clean Up Docker Volumes and Networks

```bash
docker volume prune -f
docker network prune -f
```

### Access JupyterLab Container as Root

```bash
docker exec -it --user root jupyterlab bash
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
```

### 2. **`.env`**
This file will contain your environment variables:

```dotenv
# .env

# General settings
PROJECT_NAME=data-engineering
JUPYTERLAB_VERSION=4.2.4
SPARK_VERSION=3.4.1
DELTA_VERSION=2.4.0
ICEBERG_VERSION=1.2.0

# Ports
JUPYTERLAB_PORT=8888
SPARK_UI_PORT=4045

# Docker network
NETWORK_NAME=my-network
```

### 3. **`generate-docker-compose.sh`**

This script will generate the `docker-compose.yml` file based on your `.env` variables.

### 4. **`before_docker-compose.sh`**

This script ensures that the necessary directories are created and permissions are set correctly:

```bash
#!/bin/bash

# Create directories if they do not exist
mkdir -p ./shared-workspace
mkdir -p ./data/delta_lake

# Set permissions for the directories
chmod -R 777 ./shared-workspace
chmod -R 777 ./data/delta_lake

echo "Directories and permissions set successfully."
```

### 5. **Common Docker Commands**

Use these commands to manage your Docker environment:

```bash
# Stop all containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all volumes
docker volume prune -f

# Remove all networks
docker network prune -f

# Build and run Docker Compose
docker compose -f docker-compose.yml up --remove-orphans --build -d

# Build Images Without Cache
docker compose -f docker-compose.yml build --no-cache

# Bring Up Containers
docker compose -f docker-compose.yml up --remove-orphans -d

# Access JupyterLab container as root
docker exec -it --user root jupyterlab bash
```

With this setup, you’ll have a robust development environment for Apache Spark and Delta Lake in Docker, ready for use with JupyterLab.