# Kyros - Data Platform at the Right Scale

Deploy the right architecture at the right time. Start simple, scale when needed.

```
██╗  ██╗██╗   ██╗██████╗  ██████╗ ███████╗
██║ ██╔╝╚██╗ ██╔╝██╔══██╗██╔═══██╗██╔════╝
█████╔╝  ╚████╔╝ ██████╔╝██║   ██║███████╗
██╔═██╗   ╚██╔╝  ██╔══██╗██║   ██║╚════██║
██║  ██╗   ██║   ██║  ██║╚██████╔╝███████║
╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

**Right tool • Right time • Right cost**

## Quick Start

### Option 1: Web Deployment Interface (Recommended)
```bash
cd poc
pip install -r requirements.txt
python run.py
```
Open **http://localhost:5003** - Select components, review config, deploy with real-time logs.

### Option 2: Interactive CLI
```bash
./kyros-cli.py
```

### Option 3: Manual Preset
```bash
cp presets/level-1.env .env
./generate-docker-compose.sh
docker compose up -d
```

Access the dashboard at **http://localhost:5005**

## Architecture Levels

| Level | Name | Stack | Data Size | Cost/Month |
|-------|------|-------|-----------|------------|
| **0** | Local | DuckDB + dbt | < 50 GB | $0 |
| **1** | Team | + PostgreSQL + Dagster + Superset | < 500 GB | $20-100 |
| **2** | Data Lake | + MinIO + Delta Lake + JupyterLab | < 1 TB | $50-150 |
| **3** | Distributed | + Spark + Trino | 1+ TB | $150-500 |
| **4** | Enterprise | + Flink + Kafka + SSO | Any | $500+ |

### Do You Need Spark?

| Data Size | Recommendation |
|-----------|----------------|
| < 10 GB | PostgreSQL + dbt or DuckDB. Spark is overkill. |
| 10-100 GB | DuckDB or warehouse + dbt. Spark optional. |
| 100 GB - 1 TB | Warehouse + dbt. Spark starts making sense. |
| 1+ TB | Spark is justified. Consider Trino for federated queries. |

## Components

### Data & Processing
| Component | Description | Port | Level |
|-----------|-------------|------|-------|
| PostgreSQL | Relational database | 5432 | 1+ |
| MinIO | S3-compatible object storage | 9001 | 2+ |
| Trino | Federated SQL query engine | 8082 | 3+ |
| Spark | Distributed processing | 8080 | 3+ |
| Kafka | Event streaming platform | 9092 | 4+ |
| Flink | Stream processing | 8081 | 4+ |

### Orchestration & BI
| Component | Description | Port | Level |
|-----------|-------------|------|-------|
| Dagster | Data orchestration | 3000 | 1+ |
| Superset | BI & visualization | 8088 | 1+ |
| dbt | SQL transformations | CLI | 0+ |

### Development Tools
| Component | Description | Port | Level |
|-----------|-------------|------|-------|
| JupyterLab | Notebooks & analysis | 8888 | 2+ |
| Code Server | VS Code in browser | 8083 | 2+ |
| CloudBeaver | Database UI | 8978 | 1+ |
| SQLPad | SQL editor | 3001 | 1+ |

### Infrastructure
| Component | Description | Port | Level |
|-----------|-------------|------|-------|
| Kyros Dashboard | Platform control panel | 5000 | 1+ |
| Portainer | Container management | 9000 | 1+ |
| Grafana | Monitoring dashboards | 3002 | 2+ |

## Usage

### Interactive CLI

The CLI provides an interactive interface with GitLab-style build logs:

```bash
./kyros-cli.py
```

Options:
- **deploy** - Select components and deploy
- **stop** - Stop all running services
- **status** - Show running containers
- **levels** - View architecture levels

### Using Presets

```bash
# Level 1: Team (PostgreSQL + Dagster + Superset)
cp presets/level-1.env .env

# Level 2: Data Lake (+ MinIO + JupyterLab)
cp presets/level-2.env .env

# Level 3: Distributed (+ Spark + Trino)
cp presets/level-3.env .env

# Level 4: Enterprise (+ Kafka + Flink)
cp presets/level-4.env .env

# Generate and deploy
./generate-docker-compose.sh
docker compose up -d
```

### Custom Configuration

Edit `.env` to enable/disable specific components:

```bash
# Toggle components
INCLUDE_POSTGRES=true
INCLUDE_DAGSTER=true
INCLUDE_SUPERSET=true
INCLUDE_MINIO=false
INCLUDE_JUPYTERLAB=true
INCLUDE_TRINO=false
INCLUDE_KAFKA=false
INCLUDE_FLINK=false

# Spark workers (Level 3+)
WORKERS=2

# Resource allocation
SPARK_WORKER_MEMORY=2G
SPARK_EXECUTOR_MEMORY=2G
SPARK_WORKER_CORES=2
```

## Dashboard

The Kyros Dashboard (http://localhost:5000) provides:

- **Service Status** - Real-time health monitoring
- **System Stats** - CPU, memory, disk usage
- **Quick Access** - Links to all platform services
- **Decision Helper** - Guidance on when to scale

## Common Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f [service-name]

# Rebuild specific service
docker compose up -d --build [service-name]

# Check status
docker compose ps

# Scale Spark workers
docker compose up -d --scale spark-worker=3
```

## Project Structure

```
kyros/
├── poc/                   # Web Deployment Interface
│   ├── app/
│   │   ├── templates/     # config.html, summary.html (real-time logs)
│   │   ├── routes.py      # Flask routes + Socket.IO
│   │   └── socketio.py    # Real-time log streaming
│   └── run.py             # Entry point
├── kyros-cli.py           # Interactive CLI (Rich TUI)
├── generate-docker-compose.sh  # Compose generator
├── .env                   # Active configuration
├── presets/               # Level presets
│   ├── level-0.env        # Local (DuckDB + dbt)
│   ├── level-1.env        # Team (+ PostgreSQL, Dagster, Superset)
│   ├── level-2.env        # Data Lake (+ MinIO, JupyterLab)
│   ├── level-3.env        # Distributed (+ Spark, Trino)
│   └── level-4.env        # Enterprise (+ Kafka, Flink, SSO)
├── services/              # Modular service definitions
│   ├── postgres.yml
│   ├── dagster.yml
│   ├── spark.yml
│   └── ...
├── docker/                # Dockerfiles & configs
│   ├── kyros/             # Dashboard app
│   ├── jupyterlab/
│   ├── spark/
│   └── ...
└── VISION.md              # Project philosophy & roadmap
```

## The Problem We Solve

The data engineering industry has an over-engineering problem. Companies with 10GB deploy Spark clusters. Startups paying $15k/month for Databricks could run on DuckDB.

**Every vendor says "use us." Nobody says "you don't need us yet."**

Kyros is different: Start simple. Scale when justified. Know the difference.

## Philosophy

1. **Complexity is a cost** - Every service added is operational burden. Justify it.
2. **Ready to scale, not already scaled** - Have the path, don't walk it prematurely.
3. **Teach the trade-offs** - Don't just provide tools, explain when to use them.
4. **Accessible by default** - A student and a startup should both find value here.
5. **Honest about limitations** - This is a learning and launching platform, not enterprise software.

## Who This Is For

- **Students** learning data engineering without cloud bills
- **Bootstrapped startups** who need results, not impressive architecture
- **Career switchers** building portfolio projects
- **Small teams** who want to grow into complexity, not start with it
- **Anyone** tired of over-engineering

## Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for CLI)
- 8GB+ RAM recommended (16GB+ for Level 3+)

## Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| PostgreSQL | kyros | kyros_dev |
| Superset | admin | admin |
| MinIO | kyros | kyros_dev |

**Note:** Change these for production deployments.

## Contributing

Contributions welcome! Feel free to open an issue or submit a pull request.

## License

MIT License
