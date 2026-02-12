#!/bin/bash
# ===================
# AI-Across Restore Script
# ===================
# Restores from a backup created by backup.sh.
#
# Usage: ./restore.sh /backups/20260212_020000
#
# Environment variables (with defaults):
#   DB_USER   - PostgreSQL user (default: aiacross)
#   DB_NAME   - PostgreSQL database (default: aiacross)
#   DB_HOST   - PostgreSQL host (default: db)
#   DB_PORT   - PostgreSQL port (default: 5432)

set -euo pipefail

# Configuration
DB_USER="${DB_USER:-aiacross}"
DB_NAME="${DB_NAME:-aiacross}"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"

# Validate arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <backup-directory>"
    echo "Example: $0 /backups/20260212_020000"
    exit 1
fi

BACKUP_PATH="$1"

if [ ! -d "${BACKUP_PATH}" ]; then
    echo "ERROR: Backup directory not found: ${BACKUP_PATH}"
    exit 1
fi

# Validate backup contents
echo "=== AI-Across Restore ==="
echo "Backup: ${BACKUP_PATH}"
echo ""
echo "Contents:"
ls -lh "${BACKUP_PATH}/"
echo ""

if [ -f "${BACKUP_PATH}/metadata.json" ]; then
    echo "Metadata:"
    cat "${BACKUP_PATH}/metadata.json"
    echo ""
fi

# Confirmation prompt
echo "WARNING: This will OVERWRITE current data."
echo "  - PostgreSQL database '${DB_NAME}' will be dropped and recreated"
echo "  - Upload files will be replaced"
echo "  - ChromaDB vectors will be replaced"
echo ""
read -p "Are you sure you want to proceed? (type 'yes' to confirm): " CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo ""

# 1. Stop the backend to prevent data changes during restore
echo "[1/5] Stopping backend..."
if command -v docker &> /dev/null; then
    docker stop aiacross-backend 2>/dev/null || true
fi

# 2. Restore PostgreSQL
echo "[2/5] Restoring PostgreSQL..."
if [ ! -f "${BACKUP_PATH}/postgres.dump" ]; then
    echo "  ERROR: postgres.dump not found in backup"
    exit 1
fi

if command -v docker &> /dev/null; then
    # Drop and recreate the database
    docker exec aiacross-db psql -U "${DB_USER}" -d postgres \
        -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${DB_NAME}' AND pid <> pg_backend_pid();" 2>/dev/null || true
    docker exec aiacross-db dropdb -U "${DB_USER}" --if-exists "${DB_NAME}"
    docker exec aiacross-db createdb -U "${DB_USER}" "${DB_NAME}"

    # Restore from dump
    cat "${BACKUP_PATH}/postgres.dump" | docker exec -i aiacross-db pg_restore \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --no-owner \
        --no-privileges \
        --clean \
        --if-exists 2>/dev/null || true
else
    PGPASSWORD="${DB_PASSWORD:-}" dropdb -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" --if-exists "${DB_NAME}"
    PGPASSWORD="${DB_PASSWORD:-}" createdb -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" "${DB_NAME}"
    PGPASSWORD="${DB_PASSWORD:-}" pg_restore \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --no-owner \
        --no-privileges \
        --clean \
        --if-exists \
        "${BACKUP_PATH}/postgres.dump" 2>/dev/null || true
fi
echo "  PostgreSQL restored"

# 3. Restore uploads
echo "[3/5] Restoring uploads..."
if [ -f "${BACKUP_PATH}/uploads.tar.gz" ]; then
    if command -v docker &> /dev/null; then
        gunzip -c "${BACKUP_PATH}/uploads.tar.gz" | docker cp - aiacross-backend:/app/data/
    else
        rm -rf /app/data/uploads
        tar -xzf "${BACKUP_PATH}/uploads.tar.gz" -C /app/data
    fi
    echo "  Uploads restored"
else
    echo "  No uploads archive found (skipping)"
fi

# 4. Restore ChromaDB
echo "[4/5] Restoring ChromaDB..."
if [ -f "${BACKUP_PATH}/chroma.tar.gz" ]; then
    if command -v docker &> /dev/null; then
        gunzip -c "${BACKUP_PATH}/chroma.tar.gz" | docker cp - aiacross-backend:/app/data/
    else
        rm -rf /app/data/chroma
        tar -xzf "${BACKUP_PATH}/chroma.tar.gz" -C /app/data
    fi
    echo "  ChromaDB restored"
else
    echo "  No chroma archive found (skipping)"
fi

# 5. Restart backend and verify
echo "[5/5] Restarting backend..."
if command -v docker &> /dev/null; then
    docker start aiacross-backend
    echo "  Waiting for health check..."
    sleep 10

    # Verify health
    HEALTH=$(docker exec aiacross-backend curl -sf http://localhost:8000/health 2>/dev/null || echo "FAILED")
    if echo "${HEALTH}" | grep -q "healthy"; then
        echo "  Backend is healthy"
    else
        echo "  WARNING: Backend health check failed. Check logs: docker logs aiacross-backend"
    fi
fi

echo ""
echo "=== Restore Complete ==="
echo "Restored from: ${BACKUP_PATH}"
echo ""
