from fastapi.testclient import TestClient

from vespera.api.main import app


def test_metrics_counts_requests_by_route():
    client = TestClient(app)
    client.get("/healthz")
    body = client.get("/metrics").text
    assert 'route="/healthz"' in body