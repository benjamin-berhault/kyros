#!/bin/bash
# Kyros Backup Script
# Usage: ./scripts/backup.sh [component] [output_dir]
#
# Components: postgres, minio, grafana, all
# Default output: ./backups/YYYY-MM-DD_HH-MM-SS/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPONENT="${1:-all}"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="${2:-$PROJECT_DIR/backups/$TIMESTAMP}"

# Load environment
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

# Default values
POSTGRES_USER="${POSTGRES_USER:-kyros}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-kyros_dev}"
MINIO_ROOT_USER="${MINIO_ROOT_USER:-kyros}"
MINIO_ROOT_PASSWORD="${MINIO_ROOT_PASSWORD:-kyros_dev}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Create backup directory
mkdir -p "$BACKUP_DIR"
log_info "Backup directory: $BACKUP_DIR"

backup_postgres() {
    log_info "Backing up PostgreSQL..."

    if ! docker ps --format '{{.Names}}' | grep -q '^postgres$'; then
        log_warn "PostgreSQL container not running, skipping..."
        return 1
    fi

    # Backup all databases
    docker exec postgres pg_dumpall -U "$POSTGRES_USER" > "$BACKUP_DIR/postgres_all.sql"

    # Also backup individual databases
    for db in $(docker exec postgres psql -U "$POSTGRES_USER" -t -c "SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres';"); do
        db=$(echo "$db" | tr -d ' ')
        if [ -n "$db" ]; then
            log_info "  Backing up database: $db"
            docker exec postgres pg_dump -U "$POSTGRES_USER" "$db" > "$BACKUP_DIR/postgres_${db}.sql"
        fi
    done

    # Compress
    gzip "$BACKUP_DIR"/postgres_*.sql

    log_info "PostgreSQL backup complete"
}

backup_minio() {
    log_info "Backing up MinIO..."

    if ! docker ps --format '{{.Names}}' | grep -q '^minio$'; then
        log_warn "MinIO container not running, skipping..."
        return 1
    fi

    mkdir -p "$BACKUP_DIR/minio"

    # Use mc (MinIO client) to mirror data
    docker run --rm --network my-network \
        -v "$BACKUP_DIR/minio:/backup" \
        minio/mc:latest \
        /bin/sh -c "
            mc alias set kyros http://minio:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD &&
            mc mirror kyros/ /backup/
        " 2>/dev/null || {
        log_warn "MinIO backup failed - mc client error"
        return 1
    }

    # Compress
    tar -czf "$BACKUP_DIR/minio.tar.gz" -C "$BACKUP_DIR" minio
    rm -rf "$BACKUP_DIR/minio"

    log_info "MinIO backup complete"
}

backup_grafana() {
    log_info "Backing up Grafana..."

    if ! docker ps --format '{{.Names}}' | grep -q '^grafana$'; then
        log_warn "Grafana container not running, skipping..."
        return 1
    fi

    mkdir -p "$BACKUP_DIR/grafana"

    # Copy Grafana data
    docker cp grafana:/var/lib/grafana "$BACKUP_DIR/grafana/data" 2>/dev/null || {
        log_warn "Could not copy Grafana data directory"
    }

    # Export dashboards via API
    GRAFANA_URL="http://localhost:3002"
    GRAFANA_AUTH="admin:${GRAFANA_PASSWORD:-admin}"

    mkdir -p "$BACKUP_DIR/grafana/dashboards"

    # Get all dashboard UIDs
    curl -s -u "$GRAFANA_AUTH" "$GRAFANA_URL/api/search?type=dash-db" 2>/dev/null | \
        grep -o '"uid":"[^"]*"' | cut -d'"' -f4 | while read -r uid; do
        if [ -n "$uid" ]; then
            curl -s -u "$GRAFANA_AUTH" "$GRAFANA_URL/api/dashboards/uid/$uid" > \
                "$BACKUP_DIR/grafana/dashboards/${uid}.json" 2>/dev/null
        fi
    done

    # Compress
    tar -czf "$BACKUP_DIR/grafana.tar.gz" -C "$BACKUP_DIR" grafana
    rm -rf "$BACKUP_DIR/grafana"

    log_info "Grafana backup complete"
}

backup_dagster() {
    log_info "Backing up Dagster..."

    # Dagster uses PostgreSQL for storage, which is covered by postgres backup
    # Just backup the workspace directory

    DAGSTER_WORKSPACE="${DAGSTER_WORKSPACE:-kyros}"
    DAGSTER_DIR="$PROJECT_DIR/data/orchestrate/dagster/$DAGSTER_WORKSPACE"

    if [ -d "$DAGSTER_DIR" ]; then
        tar -czf "$BACKUP_DIR/dagster_workspace.tar.gz" -C "$PROJECT_DIR/data/orchestrate/dagster" "$DAGSTER_WORKSPACE"
        log_info "Dagster workspace backup complete"
    else
        log_warn "Dagster workspace directory not found, skipping..."
    fi
}

# Main backup logic
case "$COMPONENT" in
    postgres)
        backup_postgres
        ;;
    minio)
        backup_minio
        ;;
    grafana)
        backup_grafana
        ;;
    dagster)
        backup_dagster
        ;;
    all)
        backup_postgres || true
        backup_minio || true
        backup_grafana || true
        backup_dagster || true
        ;;
    *)
        log_error "Unknown component: $COMPONENT"
        echo "Usage: $0 [postgres|minio|grafana|dagster|all] [output_dir]"
        exit 1
        ;;
esac

# Create manifest
cat > "$BACKUP_DIR/manifest.json" << EOF
{
    "timestamp": "$TIMESTAMP",
    "component": "$COMPONENT",
    "kyros_version": "1.0.0",
    "files": $(ls -1 "$BACKUP_DIR" | grep -v manifest.json | jq -R -s -c 'split("\n") | map(select(length > 0))')
}
EOF

log_info "Backup complete: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"
