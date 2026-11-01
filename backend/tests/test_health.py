"""backend/tests/test_health.py"""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert "status" in body
    assert body["version"] == "2.0.0"
    assert "database" in body
    assert "ai_available" in body


@pytest.mark.asyncio
async def test_docs_accessible(client):
    resp = await client.get("/docs")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_redoc_accessible(client):
    resp = await client.get("/redoc")
    assert resp.status_code == 200
