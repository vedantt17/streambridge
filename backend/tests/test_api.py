from fastapi.testclient import TestClient

from app.main import app


def test_api_smoke_dashboard_and_partners():
    with TestClient(app) as client:
        health = client.get("/api/health")
        partners = client.get("/api/partners")
        dashboard = client.get("/api/dashboard/summary")

    assert health.status_code == 200
    assert partners.status_code == 200
    assert len(partners.json()) >= 8
    assert dashboard.status_code == 200
    assert dashboard.json()["partner_count"] >= 8
