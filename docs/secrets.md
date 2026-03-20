# Secret Management

Kyros supports Docker secrets for secure credential management in production environments.

## Quick Start

### 1. Generate Secrets
```bash
./scripts/generate-secrets.sh
```

This creates secure random passwords in the `secrets/` directory:
- `postgres_password.txt` - PostgreSQL database password
- `postgres_metastore_password.txt` - Hive metastore password
- `superset_password.txt` - Superset admin password
- `superset_secret_key.txt` - Superset secret key
- `minio_password.txt` - MinIO root password
- `grafana_password.txt` - Grafana admin password

### 2. Enable Secrets

Add to your `.env` file:
```bash
USE_DOCKER_SECRETS=true
```

### 3. Deploy
```bash
make generate
make up
```

## How It Works

When `USE_DOCKER_SECRETS=true`:
1. Secret files are mounted as Docker secrets
2. Services read credentials from `/run/secrets/<secret_name>`
3. Passwords are never exposed in environment variables or logs

## Manual Secret Creation

If you prefer to create secrets manually:

```bash
mkdir -p secrets

# PostgreSQL
echo "your-secure-postgres-password" > secrets/postgres_password.txt

# Superset
echo "your-secure-superset-password" > secrets/superset_password.txt
openssl rand -hex 32 > secrets/superset_secret_key.txt

# MinIO
echo "your-secure-minio-password" > secrets/minio_password.txt

# Grafana
echo "your-secure-grafana-password" > secrets/grafana_password.txt

# Set permissions
chmod 600 secrets/*.txt
```

## Secret Rotation

To rotate secrets:

1. Stop services:
   ```bash
   make down
   ```

2. Regenerate secrets:
   ```bash
   ./scripts/generate-secrets.sh
   ```

3. Restart services:
   ```bash
   make up
   ```

**Note:** Some services may require data migration when changing passwords.

## Production Recommendations

### Use External Secret Stores

For production, consider:
- **HashiCorp Vault** - Full-featured secrets management
- **AWS Secrets Manager** - If using AWS
- **Azure Key Vault** - If using Azure
- **Google Secret Manager** - If using GCP

### Security Checklist

- [ ] Generate unique secrets (never use defaults)
- [ ] Restrict file permissions (`chmod 600`)
- [ ] Never commit secrets to git
- [ ] Rotate secrets regularly
- [ ] Use TLS for all connections
- [ ] Limit network exposure

## Troubleshooting

### Secret file not found
```
Error: secrets/postgres_password.txt not found
```
Solution: Run `./scripts/generate-secrets.sh`

### Permission denied
```
Error: Permission denied reading secret
```
Solution: Check file permissions with `ls -la secrets/`

### Service can't read secret
Some services expect specific secret formats. Check service documentation for requirements.

## File Permissions

```bash
# Recommended permissions
chmod 700 secrets/          # Directory
chmod 600 secrets/*.txt     # Files
```

## Environment Variables vs Secrets

| Aspect | Environment Variables | Docker Secrets |
|--------|----------------------|----------------|
| Storage | In memory, process env | File on tmpfs |
| Visibility | docker inspect shows them | Hidden |
| Logging | May appear in logs | Protected |
| Use case | Development | Production |
