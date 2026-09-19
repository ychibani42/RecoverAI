.PHONY: help up down watch restart logs ps clean \
	dev-backend dev-frontend install-frontend \
	ingest import-xrays sync test lint

help:
	@echo "Targets disponibles:"
	@echo "  up               - docker compose up -d --build (qdrant + mongo + backend)"
	@echo "  watch            - docker compose watch (backend con hot-reload sincronizando src/scripts)"
	@echo "  down             - docker compose down"
	@echo "  restart          - docker compose restart"
	@echo "  logs             - docker compose logs -f"
	@echo "  ps               - docker compose ps"
	@echo "  clean            - docker compose down -v (borra tambien los volumenes de datos)"
	@echo "  dev-backend      - backend local con uv + uvicorn --reload (sin Docker)"
	@echo "  dev-frontend     - frontend local con npm run dev (puerto 8080)"
	@echo "  install-frontend - npm install en frontend/"
	@echo "  sync             - uv sync --extra dev"
	@echo "  ingest           - uv run scripts/ingest_vector_db.py"
	@echo "  import-xrays     - uv run scripts/import_kaggle_xrays.py"
	@echo "  test             - uv run pytest"
	@echo "  lint             - uv run ruff check . && npm --prefix frontend run lint"

up:
	docker compose up -d --build

watch:
	docker compose watch

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

ps:
	docker compose ps

clean:
	docker compose down -v

dev-backend:
	uv run uvicorn recovery_ia.api.main:app --reload

dev-frontend:
	npm --prefix frontend run dev

install-frontend:
	npm --prefix frontend install

sync:
	uv sync --extra dev

ingest:
	uv run scripts/ingest_vector_db.py

import-xrays:
	uv run scripts/import_kaggle_xrays.py

test:
	uv run pytest

lint:
	uv run ruff check .
	npm --prefix frontend run lint
