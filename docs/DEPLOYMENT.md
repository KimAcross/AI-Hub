# Deployment Guide

This guide documents the current deployment approach for AI-Across.

## Status

- Production deployment hardening is tracked in `ROADMAP.md` Phase 8.
- CI workflow is implemented at `.github/workflows/ci.yml`.
- Phase 8 code deliverables are implemented:
  - CI/auth test baseline updates
  - structured logging + request correlation IDs
  - self-healing ingestion retries
  - backup/restore scripts and runbook
  - message feedback capture
  - workspace schema groundwork
  - per-assistant RAG guardrails

## Prerequisites

- Docker Engine 24+
- Docker Compose v2+
- Linux host recommended for production (Ubuntu 22.04+)
- Public DNS pointed to the host (for HTTPS setup)

## Required Environment

Create `.env` from `.env.example` and set at minimum:

- `DB_PASSWORD`
- `SECRET_KEY`
- `ADMIN_PASSWORD`
- `OPENROUTER_API_KEY`

Recommended:

- `CORS_ORIGINS` set to your real frontend origin(s)
- `RATE_LIMIT_*` values tuned to expected traffic
- `LOG_LEVEL` and `LOG_FORMAT` (`json` recommended)
- `BACKUP_DIR` and `BACKUP_RETENTION_DAYS`

## Development Stack

```bash
docker compose -f docker-compose.dev.yml up -d
```

Services:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Health: `http://localhost:8000/api/v1/health`

## Production Stack

```bash
docker compose up -d
```

Services:

- Nginx: ports `80/443`
- Backend: internal `8000`
- Frontend: internal static app
- PostgreSQL: internal `5432`

## Health Checks

Use:

- `/health`
- `/ready`

Example:

```bash
curl -f http://localhost/health
curl -f http://localhost/ready
```

## HTTPS (Let's Encrypt + Nginx)

Example on Ubuntu 22.04+:

```bash
sudo apt update
sudo apt install -y certbot
sudo systemctl stop nginx
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com
sudo systemctl start nginx
```

Mount certs into `docker/nginx/ssl` or point Nginx config to:
- `/etc/letsencrypt/live/your-domain.com/fullchain.pem`
- `/etc/letsencrypt/live/your-domain.com/privkey.pem`

Renewal:

```bash
sudo certbot renew --dry-run
```

After renewal, reload Nginx:

```bash
docker compose exec nginx nginx -s reload
```

## Backups

Backup/restore scripts and drill instructions are documented in `docs/BACKUP.md`.

## Troubleshooting

- Backend not healthy:
  - `docker compose logs backend`
  - verify `DATABASE_URL` and DB credentials.
- Frontend cannot call API:
  - verify Nginx proxy config in `docker/nginx/nginx.conf`.
  - verify CORS origins and exposed ports.
- Migration issues on fresh DB:
  - inspect Alembic migration `20260204_000000_003_add_admin_features.py` enum creation path.

## VPS Deployment (Ubuntu 22.04+)

1. Install Docker + Compose plugin.
2. Clone repository to `/opt/ai-across`.
3. Create `.env` with production values from `.env.example`.
4. Configure DNS A record to server IP.
5. Bring up stack:

```bash
docker compose up -d --build
```

6. Verify:
- `curl -f http://localhost/health`
- `curl -f http://localhost/ready`

7. Enable backups:
- configure `BACKUP_DIR` and `BACKUP_RETENTION_DAYS`
- apply host cron from `docs/BACKUP.md`

## Related Docs

- `README.md`
- `ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/HLD.md`
