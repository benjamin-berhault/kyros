
# Data Engineering with Apache Spark and Delta Lake
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents** 

- [Think Tank](#think-tank)
- [📝 Next steps](#-next-steps)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Common Commands](#common-commands)
- [Contributing](#contributing)
- [License](#license)
- [Project Setup](#project-setup)
- [Getting Started](#getting-started)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

This project provides a Docker-based environment for data engineering using Apache Spark and Delta Lake. The setup includes a JupyterLab instance preconfigured with Spark, Delta Lake, and other necessary tools.

## 📝 Next steps

- DBeaver data access for the 3 formats
- Orchestration with Dagster
- Hue

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
# Build Images Without Cache
docker compose -f docker-compose.yml build --no-cache

# Bring Up Containers
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

We welcome contributions! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.

## Project Setup

### 1. **Environment Variables (`.env`)**

The `.env` file contains all the environment variables needed to configure your Docker setup:

```dotenv
# General settings
# General settings
PROJECT_NAME=data-engineering
JUPYTERLAB_VERSION=4.2.4
SPARK_VERSION=3.4.1
DELTA_VERSION=2.4.0
ICEBERG_VERSION=1.2.0

# Ports
# Ports
JUPYTERLAB_PORT=8888
SPARK_UI_PORT=4045

# Docker network
# Docker network
NETWORK_NAME=my-network
```

### 2. **Generate Docker Compose (`generate-docker-compose.sh`)**

This script generates the `docker-compose.yml` file dynamically based on the variables specified in your `.env` file. Ensure to run this script before starting your Docker containers.

### 3. **Permissions Setup (`before_docker-compose.sh`)**

Run this script to ensure that the necessary directories are created and permissions are set correctly:

```bash
#!/bin/bash

# Create directories if they do not exist
# Create directories if they do not exist
mkdir -p ./shared-workspace
mkdir -p ./data/delta_lake

# Set permissions for the directories
# Set permissions for the directories
chmod -R 777 ./shared-workspace
chmod -R 777 ./data/delta_lake

echo "Directories and permissions set successfully."
```

### 4. **Common Docker Commands**

Here are some essential Docker commands for managing your environment:

```bash
# Stop all running containers
# Stop all running containers
docker stop $(docker ps -aq)

# Remove all containers
# Remove all containers
docker rm $(docker ps -aq)

# Remove all volumes
# Remove all volumes
docker volume prune -f

# Remove all networks
# Remove all networks
docker network prune -f

# Build and start the containers with Docker Compose
# Build and start the containers with Docker Compose
docker compose -f docker-compose.yml up --remove-orphans --build -d

# Build images without using cache
# Build images without using cache
docker compose -f docker-compose.yml build --no-cache

# Start containers without rebuilding
# Start containers without rebuilding
docker compose -f docker-compose.yml up --remove-orphans -d

# Access the JupyterLab container as root
# Access the JupyterLab container as root
docker exec -it --user root jupyterlab bash
```

## Getting Started

With this setup, you have a complete development environment for Apache Spark and Delta Lake within Docker, integrated seamlessly with JupyterLab.
