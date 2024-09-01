
# Data Engineering with Apache Spark and Delta Lake

This project provides a Docker-based environment for data engineering using Apache Spark and Delta Lake. The setup includes a JupyterLab instance preconfigured with Spark, Delta Lake, and other necessary tools.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
**Table of Contents** 

- [📝 Next steps](#-next-steps)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Common Commands](#common-commands)
- [Project Setup](#project-setup)
- [Contributing](#contributing)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


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
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all volumes
docker volume prune -f

# Remove all networks
docker network prune -f

# Build and start the containers with Docker Compose
docker compose -f docker-compose.yml up --remove-orphans --build -d

# Build images without using cache
docker compose -f docker-compose.yml build --no-cache

# Start containers without rebuilding
docker compose -f docker-compose.yml up --remove-orphans -d

# Access the JupyterLab container as root
docker exec -it --user root jupyterlab bash

# Lists all running Docker containers, displaying each container's ID, name, and IP address in a clear, readable format
docker ps -q | while read id; do echo -n "$id -> "; docker inspect -f '{{.Name}} -> {{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $id | sed 's/\///'; echo ""; done
```

Check sparkuser existence:
```bash
docker exec -it spark-master id sparkuser
docker exec -it spark-worker-1 id sparkuser
docker exec -it spark-worker-2 id sparkuser
docker exec -it hive-metastore id sparkuser
docker exec -it spark-thrift-server id sparkuser
docker exec -it postgres id sparkuser
```

#### Confirms that your core-site.xml is being correctly loaded by Spark within the spark-thrift-server container

Access Spark Shell
```
spark-shell
```

Verify Loading Configuration  
```java
scala> val conf = spark.sparkContext.hadoopConfiguration
conf: org.apache.hadoop.conf.Configuration = Configuration: core-default.xml, core-site.xml, mapred-default.xml, mapred-site.xml, yarn-default.xml, yarn-site.xml, __spark_hadoop_conf__.xml

scala> println(conf.get("fs.defaultFS"))  // Should print the value from core-site.xml
hdfs://namenode:9000

scala> println(conf.get("hadoop.security.group.mapping"))  // Should print the value from core-site.xml
org.apache.hadoop.security.ShellBasedUnixGroupsMapping
```

## Hive

Connection
 * Host: `localhost`
 * Port: `10000`
 * Database/Schema: `default`
 * Username: `sparkuser`
 * Password: `sparkuser_password`

## Getting Started Tutorials

* Delta Lake PySpark Python Helper Class | Working with Delta Lakes & Glue Pyspark Made Easy
  * [YouTube Video](https://www.youtube.com/watch?v=fMF6J5-KJVw&list=PLL2hlSFBmWwyg9XXo9itISuh3exPNk70O)
  * [Documentation](http://delta-lake-helper-class.s3-website-us-east-1.amazonaws.com/)
  * [GitHub Repo](https://github.com/soumilshah1995/Delta-Lake-Pyspark-Helper-Class)

* Reading Data from Hudi INC & Joining with Delta Tables using HudiStreamer & SQL-Based Transformer
  * [YouTube Video](https://www.youtube.com/watch?v=g5N-C5JbC_o)
  * [](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbVBzZjdmTHF3cVYwVnlrLV8zMFpNbWFUbjFiZ3xBQ3Jtc0ttZk9QXzBYLUxUUG5FZ0prUS14eEdRZXQ0djA3Z1lMWXFjdThYYndlNlBYdUVETmdjT2lOeDhoX2ZQR19qT2l1Ql83Vnh6SVkwR2VGY1VabXFaa19BZmxrUF96ZF9FVU5ZbkNCQ3VwcDBqRmtPR2VEUQ&q=https%3A%2F%2Fgithub.com%2Fsoumilshah1995%2FHudi-delta-etl-deltastreamer%2Ftree%2Fmain&v=g5N-C5JbC_o)

`/opt/bitnami/spark/sbin/start-thriftserver.sh`
```sh
#!/usr/bin/env bash

#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#
# Shell script for starting the Spark SQL Thrift server

# Enter posix mode for bash
set -o posix

if [ -z "${SPARK_HOME}" ]; then
  export SPARK_HOME="$(cd "`dirname "$0"`"/..; pwd)"
fi

# NOTE: This exact class name is matched downstream by SparkSubmit.
# Any changes need to be reflected there.
CLASS="org.apache.spark.sql.hive.thriftserver.HiveThriftServer2"

function usage {
  echo "Usage: ./sbin/start-thriftserver [options] [thrift server options]"
  pattern="usage"
  pattern+="\|Spark assembly has been built with Hive"
  pattern+="\|NOTE: SPARK_PREPEND_CLASSES is set"
  pattern+="\|Spark Command: "
  pattern+="\|======="
  pattern+="\|--help"
  pattern+="\|Using Spark's default log4j profile:"
  pattern+="\|^log4j:"
  pattern+="\|Started daemon with process name"
  pattern+="\|Registered signal handler for"

  "${SPARK_HOME}"/bin/spark-submit --help 2>&1 | grep -v Usage 1>&2
  echo
  echo "Thrift server options:"
  "${SPARK_HOME}"/bin/spark-class $CLASS --help 2>&1 | grep -v "$pattern" 1>&2
}

if [[ "$@" = *--help ]] || [[ "$@" = *-h ]]; then
  usage
  exit 1
fi

export SUBMIT_USAGE_FUNCTION=usage

exec "${SPARK_HOME}"/sbin/spark-daemon.sh submit $CLASS 1 --name "Thrift JDBC/ODBC Server" "$@"
```

## Contributing

We welcome contributions! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
