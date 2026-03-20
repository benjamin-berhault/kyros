#!/bin/bash
# Generate secure random secrets for Kyros deployment
# Usage: ./scripts/generate-secrets.sh

set -e

SECRETS_DIR="$(dirname "$0")/../secrets"

# Create secrets directory if it doesn't exist
mkdir -p "$SECRETS_DIR"

# Function to generate random password
generate_password() {
    openssl rand -base64 32 | tr -d '/+=' | head -c 32
}

# Function to generate secret key
generate_secret_key() {
    openssl rand -hex 32
}

echo "Generating secrets in $SECRETS_DIR..."

# PostgreSQL
echo "$(generate_password)" > "$SECRETS_DIR/postgres_password.txt"
echo "$(generate_password)" > "$SECRETS_DIR/postgres_metastore_password.txt"

# Superset
echo "$(generate_password)" > "$SECRETS_DIR/superset_password.txt"
echo "$(generate_secret_key)" > "$SECRETS_DIR/superset_secret_key.txt"

# MinIO
echo "$(generate_password)" > "$SECRETS_DIR/minio_password.txt"

# Grafana
echo "$(generate_password)" > "$SECRETS_DIR/grafana_password.txt"

# Set restrictive permissions
chmod 600 "$SECRETS_DIR"/*.txt

echo ""
echo "Secrets generated successfully!"
echo ""
echo "Files created:"
ls -la "$SECRETS_DIR"
echo ""
echo "IMPORTANT: Add 'secrets/' to your .gitignore (already configured)"
echo ""
echo "To use secrets, set USE_DOCKER_SECRETS=true in your .env file"
