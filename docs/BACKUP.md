# Backup & Restore

This document covers the backup and restore procedures for AI-Across.

## What Gets Backed Up

| Component | Contents | Backup Format |
|-----------|----------|---------------|
| PostgreSQL | All tables (assistants, conversations, messages, users, etc.) | `pg_dump` custom format (`.dump`) |
| Uploads | Knowledge base files (PDFs, DOCX, TXT, MD) | Compressed tar (`.tar.gz`) |
| ChromaDB | Vector embeddings for RAG retrieval | Compressed tar (`.tar.gz`) |

## Backup Schedule

| Setting | Default | Description |
|---------|---------|-------------|
| `BACKUP_SCHEDULE` | `0 2 * * *` | Daily at 2:00 AM |
| `BACKUP_RETENTION_DAYS` | `7` | Keep last 7 days of backups |
| `BACKUP_DIR` | `/backups` | Base directory for backup storage |

## Running Backups

### Manual Backup

From the host machine where Docker is running:

```bash
./docker/scripts/backup.sh
```

### Automated via Cron

Add to your host crontab (`crontab -e`):

```cron
# AI-Across daily backup at 2 AM
0 2 * * * BACKUP_DIR=/backups BACKUP_RETENTION_DAYS=7 DB_PASSWORD=your-db-password /path/to/ai-hub/docker/scripts/backup.sh >> /var/log/aiacross-backup.log 2>&1
```

### Environment Variables

Set these in your shell or crontab before running `backup.sh`:

```bash
export BACKUP_DIR=/backups             # Where to store backups
export BACKUP_RETENTION_DAYS=7         # Days to keep
export DB_USER=aiacross                # PostgreSQL user
export DB_NAME=aiacross                # PostgreSQL database
export DB_PASSWORD=your-db-password    # PostgreSQL password (for non-Docker runs)
```

## Backup Output

Each backup creates a timestamped directory:

```
/backups/
├── 20260212_020000/
│   ├── postgres.dump      # PostgreSQL database dump
│   ├── uploads.tar.gz     # Uploaded knowledge files
│   ├── chroma.tar.gz      # ChromaDB vector data
│   └── metadata.json      # Backup metadata
├── 20260211_020000/
│   └── ...
```

## Restore Procedure

### Step 1: Identify the Backup

List available backups:

```bash
ls -la /backups/
```

### Step 2: Run Restore

```bash
./docker/scripts/restore.sh /backups/20260212_020000
```

The script will:
1. Show backup contents and ask for confirmation
2. Stop the backend container
3. Drop and recreate the PostgreSQL database
4. Restore uploads and ChromaDB data
5. Restart the backend and verify health

### Step 3: Verify

After restore, verify:
- Health endpoint: `curl http://localhost/health`
- Login to the application and check data
- Verify an assistant's knowledge files are accessible

## Restore Drill

Perform a restore drill quarterly to ensure backups are valid:

1. **Create a fresh backup:** `./docker/scripts/backup.sh`
2. **Note current state:** Count of assistants, conversations, users
3. **Run restore** from the backup just created
4. **Verify counts match** and the application functions correctly
5. **Document results** with date and any issues encountered

## Troubleshooting

### Backup fails with "permission denied"

Ensure the backup directory is writable:

```bash
mkdir -p /backups
chmod 755 /backups
```

### Restore fails with "database in use"

The restore script terminates active connections automatically. If it still fails, stop all containers first:

```bash
docker compose stop backend
./docker/scripts/restore.sh /backups/20260212_020000
docker compose up -d
```

### Large backup sizes

ChromaDB vectors can grow large with many files. Monitor backup sizes and adjust retention accordingly. For a typical deployment with ~100 knowledge files, expect ~500MB per backup.
