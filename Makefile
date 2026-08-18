.PHONY: up down logs test build seed

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

test:
	cd backend && python -m pytest -q

build:
	cd frontend && npm install && npm run build

monitoring:
	docker compose --profile monitoring up -d uptime-kuma

production:
	docker compose --profile production --profile monitoring up -d --build
