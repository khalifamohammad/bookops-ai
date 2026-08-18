#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/bookops-ai/bookops-ai}"
BACKUP_DIR="${BACKUP_DIR:-/opt/bookops-backups}"
KEEP_DAYS="${KEEP_DAYS:-14}"
STAMP="$(date +%Y%m%d_%H%M%S)"

cd "$APP_DIR"
mkdir -p "$BACKUP_DIR"

docker compose exec -T db pg_dump -U "${POSTGRES_USER:-bookops}" "${POSTGRES_DB:-bookops}" | gzip > "$BACKUP_DIR/bookops_${STAMP}.sql.gz"
find "$BACKUP_DIR" -type f -name 'bookops_*.sql.gz' -mtime "+$KEEP_DAYS" -delete
printf 'Backup created: %s\n' "$BACKUP_DIR/bookops_${STAMP}.sql.gz"
