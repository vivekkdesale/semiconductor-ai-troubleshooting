.PHONY: install test lint up down migrate ingest

install:
	python3 -m venv .venv
	.venv/bin/pip install -e '.[dev]'

test:
	.venv/bin/pytest

lint:
	.venv/bin/ruff check .

up:
	docker compose up --build -d

down:
	docker compose down

migrate:
	docker compose run --rm api alembic upgrade head

ingest:
	docker compose run --rm api secom-ingest --features /data/raw/secom.data --labels /data/raw/secom_labels.data

