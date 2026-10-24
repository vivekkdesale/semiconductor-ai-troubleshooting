from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from semiconductor.db import get_session
from semiconductor.main import create_app


def test_root_metadata():
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "semiconductor-ai-troubleshooting"
    assert response.json()["docs"] == "/docs"


def test_health_uses_database_dependency():
    app = create_app()
    session = MagicMock()
    app.dependency_overrides[get_session] = lambda: session
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
    session.execute.assert_called_once()
