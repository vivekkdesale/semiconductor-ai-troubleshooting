# Option B architecture

Phase 1 establishes replaceable interfaces around an open industrial data stack:

```text
UCI SECOM files -> validated adapter -> FastAPI service -> TimescaleDB/PostgreSQL
                                             |        -> Neo4j knowledge graph
                                             |        -> Qdrant knowledge vectors
                                             +--------> Grafana operations view
```

## Responsibilities

- **TimescaleDB/PostgreSQL** is the system of record for runs, quality outcomes,
  investigations, and long-form sensor history. This avoids split transactions
  between a historian and operational database during Phase 1.
- **Neo4j** is provisioned for equipment, sensor, failure-mode, and causal
  relationships. Phase 1 creates its integration boundary and schema bootstrap.
- **Qdrant** is provisioned for manuals, procedures, incident reports, and future
  GraphRAG retrieval. Embedding and LLM providers remain configurable later.
- **FastAPI** owns versioned application endpoints. The same service boundary is
  intended to expose MCP tools in Phase 2.
- **Grafana** reads TimescaleDB for engineering dashboards.

The dataset adapter emits domain records rather than database rows, so a future
fab historian, MES, or other public dataset can use the same persistence path.

