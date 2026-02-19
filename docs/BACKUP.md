# Backup and Restore Runbook

This runbook covers daily backups for:
- PostgreSQL data
- Uploaded files (`UPLOAD_DIR`)
- ChromaDB persistence (`CHROMA_PERSIST_DIR`)

## Prerequisites

- Docker Compose stack is running (`db`, `backend`).
- `DB_USER`, `DB_PASSWORD`, `DB_NAME` are set.
- Backup scripts exist:
  - `docker/scripts/backup.sh`
  - `docker/scripts/restore.sh`

## Configuration

Set in `.env` (or environment):

```env
BACKUP_DIR=./backups
BACKUP_RETENTION_DAYS=7
```

Optional overrides:

```env
DB_HOST=db
DB_PORT=5432
UPLOADS_DIR=/app/data/uploads
CHROMA_DIR=/app/data/chroma
```

## Run Backup Manually

From repo root:

```bash
docker compose run --rm \
  -e DB_PASSWORD="$DB_PASSWORD" \
  -e BACKUP_DIR=/backups \
  -e BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}" \
  -v "$(pwd)/backups:/backups" \
  -v backend_uploads:/app/data/uploads \
  -v backend_chroma:/app/data/chroma \
  backup sh /scripts/backup.sh
```

Each run creates `BACKUP_DIR/<timestamp>/` with:
- `postgres.dump`
- `uploads.tar.gz` (if present)
- `chroma.tar.gz` (if present)
- `manifest.txt`

## Restore Procedure

1. Pick backup folder, e.g. `./backups/20260219T120000Z`.
2. Stop write traffic to the app.
3. Run restore:

```bash
docker compose run --rm \
  -e DB_PASSWORD="$DB_PASSWORD" \
  -v "$(pwd)/backups:/backups" \
  -v backend_uploads:/app/data/uploads \
  -v backend_chroma:/app/data/chroma \
  backup sh /scripts/restore.sh /backups/20260219T120000Z
```

4. Confirm prompt by typing `RESTORE`.
5. Restart services and validate app behavior.

## Restore Drill (Required)

Run a monthly drill in non-production:
1. Take a fresh backup.
2. Restore into a clean test environment.
3. Validate:
- admin login works
- assistants and conversations are visible
- at least one RAG query returns expected context
4. Record drill date, backup timestamp, and any issues.

## Scheduling

Use host cron (recommended):

```cron
0 2 * * * cd /path/to/AI-Hub && DB_PASSWORD=... BACKUP_RETENTION_DAYS=7 docker compose run --rm -e DB_PASSWORD=$DB_PASSWORD -e BACKUP_RETENTION_DAYS=$BACKUP_RETENTION_DAYS -v /path/to/AI-Hub/backups:/backups -v backend_uploads:/app/data/uploads -v backend_chroma:/app/data/chroma backup sh /scripts/backup.sh >> /var/log/aiacross-backup.log 2>&1
```

This satisfies the daily backup + retention requirement without adding separate host tooling.
