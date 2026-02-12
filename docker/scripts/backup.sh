#!/bin/bash
# ===================
# AI-Across Backup Script
# ===================
# Backs up PostgreSQL, uploads, and ChromaDB data.
# Run manually or via cron: 0 2 * * * /path/to/backup.sh
#
# Environment variables (with defaults):
#   BACKUP_DIR          - Base directory for backups (default: /backups)
#   BACKUP_RETENTION_DAYS - Days to keep backups (default: 7)
#   DB_USER             - PostgreSQL user (default: aiacross)
#   DB_NAME             - PostgreSQL database (default: aiacross)
#   DB_HOST             - PostgreSQL host (default: db)
#   DB_PORT             - PostgreSQL port (default: 5432)
#   COMPOSE_PROJECT     - Docker Compose project name (default: auto-detect)

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
DB_USER="${DB_USER:-aiacross}"
DB_NAME="${DB_NAME:-aiacross}"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="${BACKUP_DIR}/${TIMESTAMP}"

echo "=== AI-Across Backup ==="
echo "Timestamp: ${TIMESTAMP}"
echo "Backup dir: ${BACKUP_PATH}"
echo ""

# Create backup directory
mkdir -p "${BACKUP_PATH}"

# 1. PostgreSQL backup
echo "[1/3] Backing up PostgreSQL..."
if command -v docker &> /dev/null; then
    # Running from host — exec into the db container
    docker exec aiacross-db pg_dump \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        -Fc \
        --no-owner \
        --no-privileges \
        > "${BACKUP_PATH}/postgres.dump"
else
    # Running inside a container with pg_dump available
    PGPASSWORD="${DB_PASSWORD:-}" pg_dump \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        -Fc \
        --no-owner \
        --no-privileges \
        > "${BACKUP_PATH}/postgres.dump"
fi
PG_SIZE=$(du -sh "${BACKUP_PATH}/postgres.dump" | cut -f1)
echo "  PostgreSQL dump: ${PG_SIZE}"

# 2. Uploads backup
echo "[2/3] Backing up uploads..."
if command -v docker &> /dev/null; then
    docker cp aiacross-backend:/app/data/uploads - | gzip > "${BACKUP_PATH}/uploads.tar.gz"
else
    tar -czf "${BACKUP_PATH}/uploads.tar.gz" -C /app/data uploads 2>/dev/null || echo "  No uploads directory found (skipping)"
fi
if [ -f "${BACKUP_PATH}/uploads.tar.gz" ]; then
    UPLOADS_SIZE=$(du -sh "${BACKUP_PATH}/uploads.tar.gz" | cut -f1)
    echo "  Uploads archive: ${UPLOADS_SIZE}"
fi

# 3. ChromaDB backup
echo "[3/3] Backing up ChromaDB..."
if command -v docker &> /dev/null; then
    docker cp aiacross-backend:/app/data/chroma - | gzip > "${BACKUP_PATH}/chroma.tar.gz"
else
    tar -czf "${BACKUP_PATH}/chroma.tar.gz" -C /app/data chroma 2>/dev/null || echo "  No chroma directory found (skipping)"
fi
if [ -f "${BACKUP_PATH}/chroma.tar.gz" ]; then
    CHROMA_SIZE=$(du -sh "${BACKUP_PATH}/chroma.tar.gz" | cut -f1)
    echo "  ChromaDB archive: ${CHROMA_SIZE}"
fi

# 4. Write metadata
cat > "${BACKUP_PATH}/metadata.json" <<EOF
{
  "timestamp": "${TIMESTAMP}",
  "database": "${DB_NAME}",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

# 5. Rotate old backups
echo ""
echo "Rotating backups older than ${RETENTION_DAYS} days..."
DELETED=0
if [ -d "${BACKUP_DIR}" ]; then
    for old_backup in $(find "${BACKUP_DIR}" -maxdepth 1 -mindepth 1 -type d -mtime "+${RETENTION_DAYS}" 2>/dev/null); do
        echo "  Removing: $(basename "${old_backup}")"
        rm -rf "${old_backup}"
        DELETED=$((DELETED + 1))
    done
fi
echo "  Removed ${DELETED} old backup(s)"

# Summary
TOTAL_SIZE=$(du -sh "${BACKUP_PATH}" | cut -f1)
echo ""
echo "=== Backup Complete ==="
echo "Location: ${BACKUP_PATH}"
echo "Total size: ${TOTAL_SIZE}"
echo ""
