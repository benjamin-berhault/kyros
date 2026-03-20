# Kyros - Data Engineering at the Right Scale
# Common commands for development and deployment

.PHONY: help up down build test lint clean logs status level-0 level-1 level-2 level-3 level-4 generate secrets backup restore

# Default target
help:
	@echo "Kyros - Available commands:"
	@echo ""
	@echo "  Deployment:"
	@echo "    make up          - Start services (uses current .env)"
	@echo "    make down        - Stop all services"
	@echo "    make build       - Build all images"
	@echo "    make restart     - Restart all services"
	@echo "    make logs        - Follow logs from all services"
	@echo "    make status      - Show running containers"
	@echo "    make generate    - Generate docker-compose.yml from .env"
	@echo ""
	@echo "  Level Presets:"
	@echo "    make level-0     - Deploy Level 0 (Local: DuckDB + dbt)"
	@echo "    make level-1     - Deploy Level 1 (Team: + PostgreSQL + Dagster)"
	@echo "    make level-2     - Deploy Level 2 (Data Lake: + MinIO + Jupyter)"
	@echo "    make level-3     - Deploy Level 3 (Distributed: + Spark + Trino)"
	@echo "    make level-4     - Deploy Level 4 (Enterprise: + Kafka + Flink)"
	@echo ""
	@echo "  Development:"
	@echo "    make test        - Run unit tests"
	@echo "    make test-integration - Run integration tests (requires services)"
	@echo "    make lint        - Run linter"
	@echo "    make pre-commit  - Run all pre-commit hooks"
	@echo "    make validate    - Validate YAML files"
	@echo "    make clean       - Remove generated files"
	@echo "    make install-dev - Install dev dependencies + pre-commit"
	@echo ""
	@echo "  Security:"
	@echo "    make secrets     - Generate secure random secrets"
	@echo "    make secrets-enable - Enable Docker secrets mode"
	@echo ""
	@echo "  Backup/Restore:"
	@echo "    make backup      - Backup all data (PostgreSQL, MinIO, Grafana)"
	@echo "    make restore     - Restore from backup (interactive)"
	@echo ""
	@echo "  CLI:"
	@echo "    make cli         - Run interactive CLI"

# ============================================================
# Deployment Commands
# ============================================================

generate:
	@python3 generate_compose.py

up: generate
	docker compose up -d

down:
	docker compose down

build: generate
	docker compose build

restart: down up

logs:
	docker compose logs -f

status:
	docker compose ps

# ============================================================
# Level Presets
# ============================================================

level-0:
	@echo "Deploying Level 0 (Local)..."
	cp presets/level-0.env .env
	@$(MAKE) up

level-1:
	@echo "Deploying Level 1 (Team)..."
	cp presets/level-1.env .env
	@$(MAKE) up

level-2:
	@echo "Deploying Level 2 (Data Lake)..."
	cp presets/level-2.env .env
	@$(MAKE) up

level-3:
	@echo "Deploying Level 3 (Distributed)..."
	cp presets/level-3.env .env
	@$(MAKE) up

level-4:
	@echo "Deploying Level 4 (Enterprise)..."
	cp presets/level-4.env .env
	@$(MAKE) up

# ============================================================
# Development Commands
# ============================================================

test:
	python -m pytest tests/ -v --ignore=tests/test_integration.py

test-cov:
	python -m pytest tests/ --cov=. --cov-report=html --cov-report=term --ignore=tests/test_integration.py

test-integration:
	python -m pytest tests/test_integration.py -v

lint:
	ruff check . --ignore E501

lint-fix:
	ruff check . --fix --ignore E501

validate:
	@echo "Validating YAML files..."
	@python -c "import yaml; from pathlib import Path; \
		[yaml.safe_load(f.read_text()) or print(f'✓ {f.name}') for f in Path('services').glob('*.yml')]"
	@echo "All YAML files valid!"

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

pre-commit:
	pre-commit run --all-files

clean:
	@echo "Cleaning generated files..."
	rm -f docker-compose.yml
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Done!"

# ============================================================
# CLI
# ============================================================

cli:
	./kyros-cli.py

# ============================================================
# Secrets Management
# ============================================================

secrets:
	@./scripts/generate-secrets.sh

secrets-enable:
	@echo "USE_DOCKER_SECRETS=true" >> .env
	@echo "Docker secrets enabled. Run 'make generate && make up' to apply."

# ============================================================
# Backup/Restore
# ============================================================

backup:
	@./scripts/backup.sh all

backup-postgres:
	@./scripts/backup.sh postgres

backup-minio:
	@./scripts/backup.sh minio

backup-grafana:
	@./scripts/backup.sh grafana

restore:
	@echo "Available backups:"
	@ls -1d backups/*/ 2>/dev/null || echo "  No backups found"
	@echo ""
	@read -p "Enter backup directory name: " dir && ./scripts/restore.sh "$$dir" all

# ============================================================
# Docker Utilities
# ============================================================

prune:
	@echo "Removing unused Docker resources..."
	docker system prune -f

prune-all:
	@echo "WARNING: This will remove ALL unused Docker resources including volumes!"
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] && docker system prune -af --volumes

# ============================================================
# Service-specific commands
# ============================================================

shell-postgres:
	docker exec -it postgres psql -U kyros

shell-dagster:
	docker exec -it dagster bash

logs-postgres:
	docker compose logs -f postgres

logs-dagster:
	docker compose logs -f dagster

logs-superset:
	docker compose logs -f superset
