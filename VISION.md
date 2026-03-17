# Kyros - Data Engineering at the Right Scale

## The Problem

The data engineering industry has an over-engineering problem.

Companies with 10GB of data deploy Spark clusters. Startups paying $15k/month for Databricks could run on DuckDB. Engineers copy FAANG architectures for datasets that fit in a spreadsheet.

Meanwhile:
- Students can't afford to learn real tools
- Bootstrapped startups waste runway on infrastructure
- Teams drown in operational complexity they don't need
- Nobody tells you when you actually need Spark

Every vendor says "use us." Nobody says "you don't need us yet."

## The Vision

**Start simple. Scale when justified. Know the difference.**

Kyros is a modular, progressive data platform that:
- Starts with what you actually need
- Adds complexity only when data and requirements justify it
- Teaches when each tool becomes necessary
- Lets you test the next level before committing
- Makes data engineering accessible for any budget

Not a Databricks alternative. A sane path from simple to complex.

## Progressive Architecture

### Level 0: Local (Free, handles 90% of use cases)
- DuckDB + dbt
- Runs on a laptop
- Handles up to 50GB comfortably

**Upgrade when:** Data exceeds 50GB, need team collaboration, or require warehouse features.

### Level 1: Team ($20-50/month)
- PostgreSQL + Dagster + Superset
- Basic orchestration and visualization
- Multiple data sources, scheduled jobs

**Upgrade when:** Data exceeds 500GB, need object storage, or require data lake capabilities.

### Level 2: Data Lake ($50-150/month)
- MinIO (S3-compatible) + Delta Lake
- Proper lakehouse structure
- ACID transactions on files

**Upgrade when:** Data exceeds 1TB, need distributed processing, complex ML, or streaming.

### Level 3: Distributed ($150-500/month)
- Spark cluster (single node first, then scale)
- Distributed processing
- ML workloads at scale

**Upgrade when:** Need federated queries, real-time streaming, or enterprise SSO.

### Level 4: Enterprise ($500+/month)
- Trino + Flink + Keycloak
- Full platform capabilities
- Production-grade security

## Decision Framework

### You DON'T need Spark if:
- Your largest table fits in RAM (< 64GB)
- Daily data ingestion is < 1GB
- Transformations are SQL-expressible
- Jobs can take hours to complete
- You have < 5 data sources

### You DO need Spark when:
- Single queries scan > 1TB regularly
- You need sub-minute streaming latency
- Training ML models on full datasets
- Joins between billion+ row tables

### The Honest Truth

| Data Volume | Right Starting Point |
|-------------|---------------------|
| < 10 GB | Level 0 (DuckDB + dbt) |
| 10-100 GB | Level 0 or 1 |
| 100 GB - 1 TB | Level 1 or 2 |
| 1-10 TB | Level 2 or 3 |
| 10+ TB | Level 3 or 4 |

Most companies using Databricks could run on Level 1.

## Who This Is For

- **Students** learning data engineering without cloud bills
- **Bootstrapped startups** who need results, not impressive architecture
- **Career switchers** building portfolio projects
- **Small teams** who want to grow into complexity, not start with it
- **Consultants** deploying right-sized stacks for clients
- **Anyone** tired of over-engineering

## Who This Is NOT For

- Companies needing 99.99% SLA (use managed services)
- Teams without basic Docker/Linux skills
- Organizations requiring vendor support contracts
- Anyone who needs Kubernetes today (not yet supported)

## Philosophy

1. **Complexity is a cost.** Every service added is operational burden. Justify it.
2. **Ready to scale, not already scaled.** Have the path, don't walk it prematurely.
3. **Teach the trade-offs.** Don't just provide tools, explain when to use them.
4. **Accessible by default.** A student and a startup should both find value here.
5. **Honest about limitations.** This is not enterprise software. It's a learning and launching platform.

## Project Structure

```
kyros/
├── level-0-local/          # DuckDB + dbt
├── level-1-team/           # + Postgres + Dagster + Superset
├── level-2-datalake/       # + MinIO + Delta Lake
├── level-3-distributed/    # + Spark cluster
├── level-4-enterprise/     # + Trino + Flink + SSO
├── docs/
│   ├── when-to-upgrade.md  # Decision framework
│   ├── cost-calculator.md  # Budget at each level
│   └── migration-guides/   # Level N → Level N+1
└── assessment/
    └── what-level.md       # "What level do you need?"
```

## Current State

The existing codebase (`kyros-keycloak-traefik`) represents Level 4—the full platform with 32 services.

Work needed:
- Build Levels 0-3 as standalone, working configurations
- Write decision framework documentation
- Create migration guides between levels
- Add assessment tools ("What level do you need?")
- Test suite and CI/CD

## The Name

**Kyros** (from Greek *kairos*): "the right or opportune moment"

Not just cost optimization. Using the right tool at the right time.

## Contributing

This project needs:
- Level 0-3 implementations
- Documentation writers
- Real-world testing at each level
- Feedback from the target audience

## License

Open Source (Apache 2.0)
