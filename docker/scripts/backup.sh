#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-aiacross}"
DB_NAME="${DB_NAME:-aiacross}"
UPLOADS_DIR="${UPLOADS_DIR:-/app/data/uploads}"
CHROMA_DIR="${CHROMA_DIR:-/app/data/chroma}"

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TARGET_DIR="${BACKUP_DIR}/${TIMESTAMP}"

mkdir -p "${TARGET_DIR}"

echo "[backup] starting backup at ${TIMESTAMP}"
echo "[backup] dumping postgres database ${DB_NAME} from ${DB_HOST}:${DB_PORT}"
PGPASSWORD="${DB_PASSWORD:-}" pg_dump \
  -h "${DB_HOST}" \
  -p "${DB_PORT}" \
  -U "${DB_USER}" \
  -d "${DB_NAME}" \
  -F c \
  -f "${TARGET_DIR}/postgres.dump"

if [ -d "${CHROMA_DIR}" ]; then
  tar -czf "${TARGET_DIR}/chroma.tar.gz" -C "${CHROMA_DIR}" .
fi

if [ -d "${UPLOADS_DIR}" ]; then
  tar -czf "${TARGET_DIR}/uploads.tar.gz" -C "${UPLOADS_DIR}" .
fi

cat > "${TARGET_DIR}/manifest.txt" <<EOF
timestamp=${TIMESTAMP}
db_name=${DB_NAME}
db_host=${DB_HOST}
uploads_dir=${UPLOADS_DIR}
chroma_dir=${CHROMA_DIR}
EOF

echo "[backup] rotating backups older than ${RETENTION_DAYS} days"
find "${BACKUP_DIR}" -mindepth 1 -maxdepth 1 -type d -mtime +"${RETENTION_DAYS}" -exec rm -rf {} +

echo "[backup] completed ${TARGET_DIR}"
