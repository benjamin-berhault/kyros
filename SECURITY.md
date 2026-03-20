# Security Policy

## Default Credentials Warning

This project includes **default development credentials** in preset files. These are intentionally simple for local development but **MUST be changed for any production deployment**.

### Default Credentials to Change

| Service | Default User | Default Password | Environment Variable |
|---------|-------------|------------------|---------------------|
| PostgreSQL | kyros | kyros_dev | `POSTGRES_PASSWORD` |
| Superset | admin | admin | `SUPERSET_PASSWORD` |
| MinIO | minio | minio123 | `MINIO_SECRET_KEY` |
| Portainer | admin | (set on first login) | `PORTAINER_ADMIN_PASSWORD` |
| Superset Secret | - | ChangeMeToARandomString | `SUPERSET_SECRET_KEY` |

## Production Hardening Checklist

Before deploying to production:

- [ ] Copy `.env.example` to `.env` and change ALL default passwords
- [ ] Generate a strong random string for `SUPERSET_SECRET_KEY`
- [ ] Enable TLS/HTTPS using Traefik or another reverse proxy
- [ ] Configure proper network isolation
- [ ] Set up backup procedures for PostgreSQL and MinIO
- [ ] Enable audit logging
- [ ] Review and restrict container resource limits
- [ ] Remove or secure the Portainer UI in production
- [ ] Configure proper authentication (consider Keycloak integration)

## Reporting Security Issues

If you discover a security vulnerability, please:

1. **Do not** open a public issue
2. Email the maintainers directly with details
3. Include steps to reproduce if possible

## Security Best Practices

### Environment Variables

Never commit `.env` files. The `.gitignore` is configured to exclude:
- `.env`
- `.env.local`
- `*.pem`, `*.key`
- `credentials.json`

### Secrets Management

For production, consider using:
- Docker Secrets
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault

### Network Security

- All services communicate over an internal Docker network
- Only necessary ports are exposed to the host
- Consider using Traefik for TLS termination

### Container Security

- Images are built from official base images
- Resource limits are defined to prevent DoS
- Healthchecks are configured for all services
