#!/usr/bin/env sh
set -eu

mkdir -p backups
STAMP="$(date +%Y%m%d_%H%M%S)"
FILE="backups/bookops_${STAMP}.sql.gz"

docker compose exec -T db pg_dump   -U "${POSTGRES_USER:-bookops}"   -d "${POSTGRES_DB:-bookops}" | gzip > "$FILE"

find backups -type f -name 'bookops_*.sql.gz' -mtime +14 -delete
echo "Backup written to $FILE"
