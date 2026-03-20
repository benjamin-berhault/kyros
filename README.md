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

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              KYROS PLATFORM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Superset  │  │   Grafana   │  │  JupyterLab │  │ Code Server │        │
│  │  (BI/Viz)   │  │ (Monitoring)│  │ (Notebooks) │  │  (VS Code)  │        │
│  │   :8088     │  │   :3002     │  │   :8888     │  │   :8083     │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────────────┘        │
│         │                │                │                                 │
│  ┌──────┴────────────────┴────────────────┴──────┐                         │
│  │                 Query Layer                    │                         │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────────┐│                         │
│  │  │  Trino  │  │  Spark  │  │ Spark Thrift   ││                         │
│  │  │ :8082   │  │ :8080   │  │    :10000      ││                         │
│  │  └────┬────┘  └────┬────┘  └────────────────┘│                         │
│  └───────┼────────────┼─────────────────────────┘                         │
│          │            │                                                    │
│  ┌───────┴────────────┴─────────────────────────┐                         │
│  │              Orchestration Layer              │                         │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────┐  │                         │
│  │  │ Dagster │  │   dbt   │  │    Flink    │  │                         │
│  │  │ :3000   │  │  (CLI)  │  │   :8081     │  │                         │
│  │  └────┬────┘  └────┬────┘  └──────┬──────┘  │                         │
│  └───────┼────────────┼──────────────┼─────────┘                         │
│          │            │              │                                    │
│  ┌───────┴────────────┴──────────────┴─────────┐                         │
│  │                Storage Layer                 │                         │
│  │  ┌──────────┐  ┌─────────┐  ┌─────────────┐ │                         │
│  │  │PostgreSQL│  │  MinIO  │  │    Kafka    │ │                         │
│  │  │  :5432   │  │  :9001  │  │   :9092     │ │                         │
│  │  └──────────┘  └─────────┘  └─────────────┘ │                         │
│  └─────────────────────────────────────────────┘                         │
│                                                                           │
│  ┌─────────────────────────────────────────────┐                         │
│  │            Observability Stack              │                         │
│  │  ┌────────┐  ┌──────────┐  ┌─────────────┐ │                         │
│  │  │  Loki  │◄─┤ Promtail │  │   Grafana   │ │                         │
│  │  │ :3100  │  │  (logs)  │  │  Dashboards │ │                         │
│  │  └────────┘  └──────────┘  └─────────────┘ │                         │
│  └─────────────────────────────────────────────┘                         │
│                                                                           │
│  ┌─────────────────────────────────────────────┐                         │
│  │              Management Tools               │                         │
│  │  ┌─────────┐  ┌───────────┐  ┌───────────┐ │                         │
│  │  │ Kyros   │  │ Portainer │  │CloudBeaver│ │                         │
│  │  │ :5000   │  │  :9000    │  │  :8978    │ │                         │
│  │  └─────────┘  └───────────┘  └───────────┘ │                         │
│  └─────────────────────────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Clone and Navigate
```bash
git clone https://github.com/benjamin-berhault/kyros.git
cd kyros
```

### 2. Choose Your Level

**Option A: Use Makefile (Recommended)**
```bash
make level-1    # Team: PostgreSQL + Dagster + Superset
# or
make level-2    # Data Lake: + MinIO + JupyterLab + Grafana
# or
make level-3    # Distributed: + Spark + Trino
```

**Option B: Interactive CLI**
```bash
./kyros-cli.py
```

**Option C: Manual Preset**
```bash
cp presets/level-1.env .env
make up
```

### 3. Access Services

After deployment, access services at:

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| Kyros Dashboard | http://localhost:5000 | - |
| Superset | http://localhost:8088 | admin / admin |
| Dagster | http://localhost:3000 | - |
| Grafana | http://localhost:3002 | admin / admin |
| JupyterLab | http://localhost:8888 | - |
| MinIO Console | http://localhost:9001 | kyros / kyros_dev |
| Portainer | http://localhost:9000 | (set on first login) |
| CloudBeaver | http://localhost:8978 | - |

## Architecture Levels

| Level | Name | What You Get | Data Size | Monthly Cost |
|:-----:|------|--------------|-----------|--------------|
| **0** | Local | DuckDB + dbt | < 50 GB | $0 |
| **1** | Team | + PostgreSQL + Dagster + Superset + Portainer | < 500 GB | $20-100 |
| **2** | Data Lake | + MinIO + JupyterLab + Grafana + Loki | < 1 TB | $50-150 |
| **3** | Distributed | + Spark cluster + Trino + Code Server | 1+ TB | $150-500 |
| **4** | Enterprise | + Kafka + Flink + full observability | Any | $500+ |

### Level Selection Guide

```
┌─────────────────────────────────────────────────────────────────┐
│                    DO YOU NEED SPARK?                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Data < 10 GB     →  PostgreSQL + dbt or DuckDB                │
│                      Spark is overkill.                         │
│                                                                 │
│  Data 10-100 GB   →  DuckDB or PostgreSQL + dbt                │
│                      Spark is optional.                         │
│                                                                 │
│  Data 100GB-1TB   →  PostgreSQL/warehouse + dbt                │
│                      Spark starts making sense.                 │
│                                                                 │
│  Data 1+ TB       →  Spark is justified.                       │
│                      Consider Trino for federated queries.      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Components Reference

### Storage & Data

| Component | Description | Port | Level | Use Case |
|-----------|-------------|:----:|:-----:|----------|
| **PostgreSQL** | Relational database | 5432 | 1+ | OLTP, metadata, application data |
| **MinIO** | S3-compatible object storage | 9001 | 2+ | Data lake, raw files, artifacts |
| **Kafka** | Event streaming platform | 9092 | 4+ | Real-time data pipelines |

### Processing & Query

| Component | Description | Port | Level | Use Case |
|-----------|-------------|:----:|:-----:|----------|
| **dbt** | SQL transformations | CLI | 0+ | Data modeling, ELT |
| **Spark** | Distributed processing | 8080 | 3+ | Large-scale batch processing |
| **Trino** | Federated SQL engine | 8082 | 3+ | Query across multiple sources |
| **Flink** | Stream processing | 8081 | 4+ | Real-time analytics |

### Orchestration & BI

| Component | Description | Port | Level | Use Case |
|-----------|-------------|:----:|:-----:|----------|
| **Dagster** | Data orchestration | 3000 | 1+ | Pipeline scheduling, monitoring |
| **Superset** | BI & visualization | 8088 | 1+ | Dashboards, ad-hoc queries |

### Development

| Component | Description | Port | Level | Use Case |
|-----------|-------------|:----:|:-----:|----------|
| **JupyterLab** | Notebooks | 8888 | 2+ | Data exploration, prototyping |
| **Code Server** | VS Code in browser | 8083 | 2+ | Remote development |
| **CloudBeaver** | Database UI | 8978 | 1+ | SQL queries, schema browsing |
| **SQLPad** | SQL editor | 3001 | 1+ | Quick queries, sharing |

### Observability

| Component | Description | Port | Level | Use Case |
|-----------|-------------|:----:|:-----:|----------|
| **Grafana** | Monitoring dashboards | 3002 | 2+ | Metrics, logs visualization |
| **Loki** | Log aggregation | 3100 | 2+ | Centralized logging |
| **Promtail** | Log collector | - | 2+ | Ship logs to Loki |

### Management

| Component | Description | Port | Level | Use Case |
|-----------|-------------|:----:|:-----:|----------|
| **Kyros Dashboard** | Platform control | 5000 | 1+ | Service status, quick access |
| **Portainer** | Container management | 9000 | 1+ | Docker UI, logs, shells |

## Makefile Commands

```bash
# Deployment
make up              # Start services (generates compose first)
make down            # Stop all services
make build           # Build all images
make restart         # Restart all services
make logs            # Follow logs from all services
make status          # Show running containers
make generate        # Generate docker-compose.yml from .env

# Level Presets
make level-0         # Deploy Level 0 (Local)
make level-1         # Deploy Level 1 (Team)
make level-2         # Deploy Level 2 (Data Lake)
make level-3         # Deploy Level 3 (Distributed)
make level-4         # Deploy Level 4 (Enterprise)

# Development
make test            # Run test suite
make lint            # Run linter
make validate        # Validate YAML files
make clean           # Remove generated files

# Utilities
make cli             # Run interactive CLI
make shell-postgres  # Open psql shell
make prune           # Clean unused Docker resources
```

## Configuration

### Environment Variables

Create `.env` from a preset or customize:

```bash
# Copy a preset
cp presets/level-2.env .env

# Or customize manually
cat > .env << 'EOF'
# Components
INCLUDE_POSTGRES=true
INCLUDE_DAGSTER=true
INCLUDE_SUPERSET=true
INCLUDE_MINIO=true
INCLUDE_JUPYTERLAB=true
INCLUDE_GRAFANA=true
INCLUDE_LOKI=true
INCLUDE_PROMTAIL=true
INCLUDE_TRINO=false
INCLUDE_KAFKA=false
INCLUDE_FLINK=false

# Spark workers (Level 3+)
WORKERS=0

# Resources
SPARK_WORKER_MEMORY=2G
SPARK_EXECUTOR_MEMORY=2G
SPARK_WORKER_CORES=2

# Credentials
POSTGRES_USER=kyros
POSTGRES_PASSWORD=kyros_dev
SUPERSET_ADMIN=admin
SUPERSET_PASSWORD=admin
EOF
```

### Regenerate Compose

After changing `.env`:
```bash
make generate   # or: python3 generate_compose.py
make up
```

## Project Structure

```
kyros/
├── docker/                    # Dockerfiles & service configs
│   ├── dagster/              # Dagster configuration
│   ├── grafana/              # Grafana provisioning
│   │   └── provisioning/     # Dashboards & datasources
│   ├── kyros/                # Dashboard application
│   ├── loki/                 # Loki configuration
│   ├── postgres/             # PostgreSQL initialization
│   ├── promtail/             # Promtail configuration
│   ├── spark-master/         # Spark master node
│   ├── spark-worker/         # Spark worker nodes
│   └── superset/             # Superset configuration
├── services/                  # Modular service definitions
│   ├── postgres.yml          # Database service
│   ├── dagster.yml           # Orchestration service
│   ├── superset.yml          # BI service
│   ├── grafana.yml           # Monitoring service
│   ├── loki.yml              # Log aggregation
│   ├── promtail.yml          # Log collection
│   └── ...                   # Other services
├── presets/                   # Level preset configurations
│   ├── level-0.env           # Local (DuckDB + dbt)
│   ├── level-1.env           # Team
│   ├── level-2.env           # Data Lake
│   ├── level-3.env           # Distributed
│   └── level-4.env           # Enterprise
├── tests/                     # Test suite
│   ├── test_cli.py           # CLI tests
│   └── test_generate_compose.py  # Compose generator tests
├── data/                      # Data directories (gitignored)
│   ├── data/                 # Shared data volume
│   ├── lab/                  # JupyterLab workspace
│   └── transform/            # dbt project
├── kyros-cli.py              # Interactive CLI
├── generate_compose.py        # Compose file generator
├── docker-compose.template.yml # Base template
├── Makefile                   # Common commands
└── README.md                  # This file
```

## Observability

### Viewing Logs

**Via Grafana (Recommended):**
1. Open http://localhost:3002
2. Navigate to Dashboards → Container Logs
3. Filter by service name

**Via CLI:**
```bash
make logs                    # All services
docker compose logs -f dagster  # Specific service
```

### Pre-configured Dashboards

- **Container Logs** - Search and filter logs from all services
- **Kyros Overview** - Platform health, service status, resource usage

## System Requirements

| Level | RAM | CPU | Disk |
|-------|-----|-----|------|
| 0 | 4 GB | 2 cores | 10 GB |
| 1 | 8 GB | 4 cores | 20 GB |
| 2 | 12 GB | 4 cores | 50 GB |
| 3 | 16 GB | 8 cores | 100 GB |
| 4 | 32 GB | 16 cores | 200 GB |

## The Problem We Solve

The data engineering industry has an over-engineering problem:
- Companies with 10GB deploy Spark clusters
- Startups pay $15k/month for Databricks when DuckDB would suffice
- **Every vendor says "use us." Nobody says "you don't need us yet."**

Kyros is different: **Start simple. Scale when justified. Know the difference.**

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

## Security Note

Default credentials are for development only. For production:
1. Change all passwords in `.env`
2. Enable SSL/TLS (see `docs/security.md`)
3. Configure proper network isolation
4. Review `SECURITY.md` for guidelines

## Contributing

Contributions welcome! Please read `CONTRIBUTING.md` before submitting PRs.

## License

MIT License - See `LICENSE` for details.
