from fastapi.testclient import TestClient

from vespera.api.main import app

client = TestClient(app)

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "okk"}


def test_create_target_invalid_url():
    response = client.post("/targets", json={"name": "zly", "url": "abc"})
    assert response.status_code == 422
