#!/usr/bin/env sh
set -eu

git pull --ff-only
docker compose --profile production --profile monitoring build --pull
docker compose --profile production --profile monitoring up -d
docker image prune -f
docker compose ps
