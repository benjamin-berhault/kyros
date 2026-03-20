# Traefik Reverse Proxy

Kyros includes Traefik for reverse proxy with automatic HTTPS support.

## Quick Start

### 1. Enable Traefik

Add to your `.env`:
```bash
INCLUDE_TRAEFIK=true
DOMAIN=example.com  # Your domain
```

### 2. Deploy
```bash
make generate
make up
```

## Service URLs

With Traefik enabled, access services via subdomains:

| Service | URL |
|---------|-----|
| Dashboard | https://traefik.example.com |
| Superset | https://superset.example.com |
| Dagster | https://dagster.example.com |
| Grafana | https://grafana.example.com |
| JupyterLab | https://jupyter.example.com |
| MinIO | https://minio.example.com |
| Kyros | https://kyros.example.com |

## Production Setup with Let's Encrypt

### 1. Configure DNS

Create A records pointing to your server:
```
*.example.com  →  YOUR_SERVER_IP
```

### 2. Enable Let's Encrypt

Edit `services/traefik.yml` and uncomment:
```yaml
- "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
- "--certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}"
- "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
```

### 3. Set Email

Add to `.env`:
```bash
ACME_EMAIL=admin@example.com
```

### 4. Deploy
```bash
make generate
make up
```

## Dashboard Access

The Traefik dashboard is protected by basic auth.

### Default Credentials
- Username: `admin`
- Password: `admin`

### Change Password

Generate a new password hash:
```bash
htpasswd -nb admin your-secure-password
```

Add to `.env`:
```bash
TRAEFIK_DASHBOARD_AUTH='admin:$apr1$xyz...'
```

## Adding Traefik Labels to Services

To expose a service through Traefik, add labels:

```yaml
services:
  myservice:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myservice.rule=Host(`myservice.${DOMAIN}`)"
      - "traefik.http.routers.myservice.entrypoints=websecure"
      - "traefik.http.routers.myservice.tls.certresolver=letsencrypt"
      - "traefik.http.services.myservice.loadbalancer.server.port=8080"
```

## Local Development

For local development without a domain:

### Option 1: Use localhost
```bash
DOMAIN=localhost
```

Access via: `http://superset.localhost:8088`

### Option 2: Edit /etc/hosts
```
127.0.0.1  superset.local dagster.local grafana.local
```

### Option 3: Use nip.io
```bash
DOMAIN=127.0.0.1.nip.io
```

Access via: `http://superset.127.0.0.1.nip.io`

## Architecture

```
                    ┌─────────────┐
                    │   Internet  │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │   Traefik   │
                    │  :80 :443   │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
  ┌─────┴─────┐     ┌──────┴──────┐    ┌──────┴──────┐
  │  Superset │     │   Dagster   │    │   Grafana   │
  │   :8088   │     │    :3000    │    │    :3002    │
  └───────────┘     └─────────────┘    └─────────────┘
```

## SSL/TLS Options

### Let's Encrypt (Recommended)
Automatic certificate management via ACME.

### Self-signed Certificates
For internal/testing use:
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/traefik.key \
  -out certs/traefik.crt
```

### Custom Certificates
Mount your certificates:
```yaml
volumes:
  - ./certs:/certs:ro
```

## Troubleshooting

### Certificate not generating
1. Check DNS resolves correctly
2. Verify port 443 is accessible
3. Check Traefik logs: `docker compose logs traefik`

### Service not accessible
1. Verify labels are correct
2. Check service is on `my-network`
3. Verify `traefik.enable=true`

### 404 Not Found
- Check the Host rule matches your domain
- Verify the service port is correct

## Security Considerations

- Enable HTTPS in production
- Use strong dashboard password
- Restrict dashboard access by IP if possible
- Keep Traefik updated
