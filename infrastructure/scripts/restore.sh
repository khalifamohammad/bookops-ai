#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 backups/bookops_YYYYMMDD_HHMMSS.sql.gz"
  exit 1
fi

gzip -dc "$1" | docker compose exec -T db psql   -U "${POSTGRES_USER:-bookops}"   -d "${POSTGRES_DB:-bookops}"

echo "Restore completed"
