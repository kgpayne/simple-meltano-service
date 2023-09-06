from fastapi.testclient import TestClient

from simple_meltano_service import app

client = TestClient(app)


def test_run():
    payload = {
        "extractor": {"name": "tap-carbon-intensity"},
        "loader": {"name": "target-jsonl"},
        "env_vars": [],
    }
    response = client.post("/run/", json=payload)
    assert response.status_code == 200
    assert "message" in response.json()
