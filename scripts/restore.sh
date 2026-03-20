#!/bin/bash
# Kyros Restore Script
# Usage: ./scripts/restore.sh <backup_dir> [component]
#
# Components: postgres, minio, grafana, all

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${1:-}"
COMPONENT="${2:-all}"

if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: $0 <backup_dir> [postgres|minio|grafana|dagster|all]"
    echo ""
    echo "Available backups:"
    ls -1d "$PROJECT_DIR/backups"/*/ 2>/dev/null || echo "  No backups found"
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    # Try relative to backups directory
    if [ -d "$PROJECT_DIR/backups/$BACKUP_DIR" ]; then
        BACKUP_DIR="$PROJECT_DIR/backups/$BACKUP_DIR"
    else
        echo "Error: Backup directory not found: $BACKUP_DIR"
        exit 1
    fi
fi

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
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "Restoring from: $BACKUP_DIR"

restore_postgres() {
    log_info "Restoring PostgreSQL..."

    if ! docker ps --format '{{.Names}}' | grep -q '^postgres$'; then
        log_error "PostgreSQL container not running. Start it first: make up"
        return 1
    fi

    # Find backup file
    BACKUP_FILE=""
    if [ -f "$BACKUP_DIR/postgres_all.sql.gz" ]; then
        BACKUP_FILE="$BACKUP_DIR/postgres_all.sql.gz"
    elif [ -f "$BACKUP_DIR/postgres_all.sql" ]; then
        BACKUP_FILE="$BACKUP_DIR/postgres_all.sql"
    fi

    if [ -z "$BACKUP_FILE" ]; then
        log_warn "No PostgreSQL backup found, skipping..."
        return 1
    fi

    log_warn "This will DROP and recreate all databases. Continue? (y/N)"
    read -r confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "Skipping PostgreSQL restore"
        return 0
    fi

    # Decompress if needed
    if [[ "$BACKUP_FILE" == *.gz ]]; then
        log_info "Decompressing backup..."
        gunzip -k "$BACKUP_FILE"
        BACKUP_FILE="${BACKUP_FILE%.gz}"
        CLEANUP_FILE="$BACKUP_FILE"
    fi

    # Restore
    log_info "Restoring databases..."
    docker exec -i postgres psql -U "$POSTGRES_USER" < "$BACKUP_FILE"

    # Cleanup
    if [ -n "$CLEANUP_FILE" ]; then
        rm "$CLEANUP_FILE"
    fi

    log_info "PostgreSQL restore complete"
}

restore_minio() {
    log_info "Restoring MinIO..."

    if ! docker ps --format '{{.Names}}' | grep -q '^minio$'; then
        log_error "MinIO container not running. Start it first: make up"
        return 1
    fi

    BACKUP_FILE="$BACKUP_DIR/minio.tar.gz"
    if [ ! -f "$BACKUP_FILE" ]; then
        log_warn "No MinIO backup found, skipping..."
        return 1
    fi

    log_warn "This will overwrite existing MinIO data. Continue? (y/N)"
    read -r confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "Skipping MinIO restore"
        return 0
    fi

    # Extract
    TMP_DIR=$(mktemp -d)
    tar -xzf "$BACKUP_FILE" -C "$TMP_DIR"

    # Restore using mc
    docker run --rm --network my-network \
        -v "$TMP_DIR/minio:/backup:ro" \
        minio/mc:latest \
        /bin/sh -c "
            mc alias set kyros http://minio:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD &&
            mc mirror --overwrite /backup/ kyros/
        "

    rm -rf "$TMP_DIR"

    log_info "MinIO restore complete"
}

restore_grafana() {
    log_info "Restoring Grafana..."

    if ! docker ps --format '{{.Names}}' | grep -q '^grafana$'; then
        log_error "Grafana container not running. Start it first: make up"
        return 1
    fi

    BACKUP_FILE="$BACKUP_DIR/grafana.tar.gz"
    if [ ! -f "$BACKUP_FILE" ]; then
        log_warn "No Grafana backup found, skipping..."
        return 1
    fi

    # Extract
    TMP_DIR=$(mktemp -d)
    tar -xzf "$BACKUP_FILE" -C "$TMP_DIR"

    # Restore dashboards via API
    GRAFANA_URL="http://localhost:3002"
    GRAFANA_AUTH="admin:${GRAFANA_PASSWORD:-admin}"

    if [ -d "$TMP_DIR/grafana/dashboards" ]; then
        for dashboard in "$TMP_DIR/grafana/dashboards"/*.json; do
            if [ -f "$dashboard" ]; then
                log_info "  Restoring dashboard: $(basename "$dashboard")"
                # Wrap in import format
                jq '{dashboard: .dashboard, overwrite: true}' "$dashboard" | \
                    curl -s -X POST -H "Content-Type: application/json" \
                    -u "$GRAFANA_AUTH" \
                    -d @- \
                    "$GRAFANA_URL/api/dashboards/db" > /dev/null
            fi
        done
    fi

    rm -rf "$TMP_DIR"

    log_info "Grafana restore complete"
}

restore_dagster() {
    log_info "Restoring Dagster workspace..."

    BACKUP_FILE="$BACKUP_DIR/dagster_workspace.tar.gz"
    if [ ! -f "$BACKUP_FILE" ]; then
        log_warn "No Dagster workspace backup found, skipping..."
        return 1
    fi

    DAGSTER_WORKSPACE="${DAGSTER_WORKSPACE:-kyros}"
    DAGSTER_DIR="$PROJECT_DIR/data/orchestrate/dagster"

    log_warn "This will overwrite existing Dagster workspace. Continue? (y/N)"
    read -r confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "Skipping Dagster restore"
        return 0
    fi

    mkdir -p "$DAGSTER_DIR"
    tar -xzf "$BACKUP_FILE" -C "$DAGSTER_DIR"

    log_info "Dagster workspace restore complete"
}

# Main restore logic
case "$COMPONENT" in
    postgres)
        restore_postgres
        ;;
    minio)
        restore_minio
        ;;
    grafana)
        restore_grafana
        ;;
    dagster)
        restore_dagster
        ;;
    all)
        restore_postgres || true
        restore_minio || true
        restore_grafana || true
        restore_dagster || true
        ;;
    *)
        log_error "Unknown component: $COMPONENT"
        echo "Usage: $0 <backup_dir> [postgres|minio|grafana|dagster|all]"
        exit 1
        ;;
esac

log_info "Restore complete"
