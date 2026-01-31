# Makefile for POC Manager

.PHONY: help setup start stop restart logs clean test backend-test frontend-test migrate seed

help:
	@echo "POC Manager - Available Commands"
	@echo "================================="
	@echo "make setup          - Initial setup (create .env, start services, run migrations)"
	@echo "make start          - Start all services"
	@echo "make stop           - Stop all services"
	@echo "make restart        - Restart all services"
	@echo "make logs           - View logs"
	@echo "make clean          - Clean up containers and volumes"
	@echo "make test           - Run all tests"
	@echo "make backend-test   - Run backend tests"
	@echo "make frontend-test  - Run frontend tests"
	@echo "make migrate        - Run database migrations"
	@echo "make seed           - Seed database with sample data"

setup:
	@chmod +x setup.sh
	@./setup.sh

start:
	@docker compose up -d
	@echo "✅ Services started!"

stop:
	@docker compose down
	@echo "✅ Services stopped!"

restart:
	@docker compose restart
	@echo "✅ Services restarted!"

logs:
	@docker compose logs -f

clean:
	@docker compose down -v
	@echo "✅ Cleanup complete!"

test: backend-test frontend-test

backend-test:
	@docker compose exec backend pytest -v

frontend-test:
	@echo "Frontend tests not yet implemented"

migrate:
	@docker compose exec backend alembic upgrade head
	@echo "✅ Migrations complete!"

seed:
	@docker compose exec backend python scripts/seed_data.py
	@echo "✅ Database seeded!"

backend-shell:
	@docker compose exec backend bash

frontend-shell:
	@docker compose exec frontend sh

db-shell:
	@docker compose exec db psql -U postgres -d poc_manager
