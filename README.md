# Semiconductor AI Troubleshooting — Phase 1

Production-oriented foundation for an AI-assisted semiconductor process
troubleshooting platform using the approved **Option B** architecture.

Phase 1 includes:

- Docker Compose services for TimescaleDB/PostgreSQL, Neo4j, Qdrant, FastAPI,
  and Grafana
- Alembic migrations for production runs, time-series sensor readings, and
  investigations
- A validated, idempotent UCI SECOM adapter for all 590 sensor features
- Versioned health, run, and investigation endpoints with OpenAPI documentation
- Neo4j and Qdrant bootstrap boundaries for later GraphRAG work
- Unit/API tests that run without infrastructure

See [architecture details](docs/architecture.md) for component responsibilities.

## Prerequisites

- Docker Desktop with Compose v2, or Python 3.11+
- UCI SECOM `secom.data` and `secom_labels.data` files for ingestion

## Quick start with Docker

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
curl http://localhost:8000/api/v1/health
```

The API applies migrations at startup. Open:

- API docs: <http://localhost:8000/docs>
- Grafana: <http://localhost:3000> (`admin` / `admin`; change outside local use)
- Neo4j Browser: <http://localhost:7474>
- Qdrant dashboard: <http://localhost:6333/dashboard>

## Ingest SECOM

Place the two source files in `data/raw/`, then run:

```bash
docker compose run --rm api secom-ingest \
  --features /data/raw/secom.data \
  --labels /data/raw/secom_labels.data
```

The adapter checks row alignment and the 590-feature contract, converts timestamps
to UTC, maps `-1` to `pass` and `1` to `fail`, records missing-value counts, and
uses stable identifiers so reruns do not duplicate production runs.

## Local development and tests

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
.venv/bin/ruff check .
```

## API examples

```bash
curl 'http://localhost:8000/api/v1/runs?outcome=fail&limit=20'

curl -X POST http://localhost:8000/api/v1/investigations \
  -H 'content-type: application/json' \
  -d '{"summary":"Review failed run and correlated sensor excursions"}'
```

## Repository layout

```text
src/semiconductor/       application, domain services, and adapters
migrations/              Alembic database migrations
deploy/grafana/          provisioned operational data source
tests/                   offline unit and API tests
data/raw/                local SECOM source files (ignored)
docs/                    architecture decisions
```

## Phase boundary

This phase deliberately stops at reliable ingestion, storage, service APIs, and
infrastructure boundaries. Model training, embeddings, GraphRAG orchestration,
MCP tool exposure, operator UI, authentication, and production secret management
belong to later phases.

