#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/bookops-ai/bookops-ai}"
cd "$APP_DIR"

echo "Pulling latest BookOps..."
git pull --ff-only

echo "Building containers..."
sudo -n docker compose build --pull

echo "Starting BookOps..."
sudo -n docker compose up -d

echo "Starting monitoring..."
sudo -n docker compose --profile monitoring up -d uptime-kuma

echo "Cleaning old Docker images..."
sudo -n docker image prune -f

echo "Deployment status:"
sudo -n docker compose ps

echo "Checking API..."
sleep 10
curl --fail --silent http://127.0.0.1:8000/api/health
echo
echo "BookOps deployment successful."
