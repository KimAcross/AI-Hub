#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <backup-directory>"
  exit 1
fi

BACKUP_SRC="$1"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-aiacross}"
DB_NAME="${DB_NAME:-aiacross}"
UPLOADS_DIR="${UPLOADS_DIR:-/app/data/uploads}"
CHROMA_DIR="${CHROMA_DIR:-/app/data/chroma}"

if [ ! -d "${BACKUP_SRC}" ]; then
  echo "Backup directory not found: ${BACKUP_SRC}"
  exit 1
fi

if [ ! -f "${BACKUP_SRC}/postgres.dump" ]; then
  echo "Missing postgres dump in ${BACKUP_SRC}"
  exit 1
fi

echo "This will OVERWRITE database and file data."
echo "Backup source: ${BACKUP_SRC}"
read -r -p "Type RESTORE to continue: " CONFIRM

if [ "${CONFIRM}" != "RESTORE" ]; then
  echo "Restore cancelled."
  exit 1
fi

echo "[restore] restoring database ${DB_NAME}"
PGPASSWORD="${DB_PASSWORD:-}" dropdb -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" --if-exists "${DB_NAME}"
PGPASSWORD="${DB_PASSWORD:-}" createdb -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" "${DB_NAME}"
PGPASSWORD="${DB_PASSWORD:-}" pg_restore \
  -h "${DB_HOST}" \
  -p "${DB_PORT}" \
  -U "${DB_USER}" \
  -d "${DB_NAME}" \
  --clean \
  --if-exists \
  "${BACKUP_SRC}/postgres.dump"

if [ -f "${BACKUP_SRC}/uploads.tar.gz" ]; then
  echo "[restore] restoring uploads data"
  mkdir -p "${UPLOADS_DIR}"
  find "${UPLOADS_DIR}" -mindepth 1 -delete || true
  tar -xzf "${BACKUP_SRC}/uploads.tar.gz" -C "${UPLOADS_DIR}"
fi

if [ -f "${BACKUP_SRC}/chroma.tar.gz" ]; then
  echo "[restore] restoring chroma data"
  mkdir -p "${CHROMA_DIR}"
  find "${CHROMA_DIR}" -mindepth 1 -delete || true
  tar -xzf "${BACKUP_SRC}/chroma.tar.gz" -C "${CHROMA_DIR}"
fi

echo "[restore] restore complete"
