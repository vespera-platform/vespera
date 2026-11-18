import uuid

from fastapi.testclient import TestClient

from vespera.api.main import app

client = TestClient(app)


def test_readyz_with_database():
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_target_lifecycle_in_database():
    name = f"ci-{uuid.uuid4().hex[:8]}"

    created = client.post("/targets", json={"name": name, "url": "https://example.com"})
    assert created.status_code == 201
    target_id = created.json()["id"]

    fetched = client.get(f"/targets/{target_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == name

    listed = client.get("/targets")
    assert target_id in [t["id"] for t in listed.json()]

    checks = client.get(f"/targets/{target_id}/checks")
    assert checks.status_code == 200
    assert checks.json() == []

    deleted = client.delete(f"/targets/{target_id}")
    assert deleted.status_code == 204
    assert client.get(f"/targets/{target_id}").status_code == 404