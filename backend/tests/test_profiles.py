"""backend/tests/test_profiles.py"""
import pytest

@pytest.mark.asyncio
async def test_get_profile_auto_creates(client, auth_headers):
    resp = await client.get("/api/v1/profiles/me", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "user_id" in body
    assert isinstance(body.get("skills"), list)

@pytest.mark.asyncio
async def test_update_profile(client, auth_headers):
    resp = await client.put("/api/v1/profiles/me", headers=auth_headers, json={
        "full_name": "Test User",
        "email": "test@example.com",
        "skills": ["Python", "FastAPI", "Docker"],
        "languages": ["Python", "Go"],
        "experience": [
            {
                "company": "Acme Corp",
                "role": "Software Engineer",
                "duration": "2022–2024",
                "location": "Remote",
                "bullets": ["Built scalable APIs serving 1M users"]
            }
        ]
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["full_name"] == "Test User"
    assert "Python" in body["skills"]
    assert len(body["experience"]) == 1

@pytest.mark.asyncio
async def test_profile_unauthenticated(client):
    resp = await client.get("/api/v1/profiles/me")
    assert resp.status_code == 403
