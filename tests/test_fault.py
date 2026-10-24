from fastapi.testclient import TestClient

from vespera.api.main import app
from vespera.common.config import get_settings


def test_fault_rate_one_breaks_api_but_not_probes(monkeypatch):
    monkeypatch.setenv("FAULT_ERROR_RATE", "1")
    get_settings.cache_clear()
    try:
        client = TestClient(app)
        assert client.get("/").status_code == 500
        assert client.get("/healthz").status_code == 200
        assert 'route="/",status="500"' in client.get("/metrics").text
    finally:
        get_settings.cache_clear()