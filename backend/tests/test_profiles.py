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


@pytest.mark.asyncio
async def test_profile_saves_social_usernames(client, auth_headers):
    resp = await client.put("/api/v1/profiles/me", headers=auth_headers, json={
        "github_username": "octocat",
        "linkedin_username": "jane-doe",
    })
    assert resp.status_code == 200
    assert resp.json()["github_username"] == "octocat"
    assert resp.json()["linkedin_username"] == "jane-doe"


@pytest.mark.asyncio
async def test_github_repositories_require_authentication(client):
    resp = await client.post("/api/v1/profiles/github/repos", json={"github_username": "octocat"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_github_repositories_reject_invalid_username(client, auth_headers):
    resp = await client.post(
        "/api/v1/profiles/github/repos",
        headers=auth_headers,
        json={"github_username": "not/a/username"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_github_repositories_return_public_project_data(client, auth_headers, monkeypatch):
    class MockResponse:
        status_code = 200
        headers = {}

        def json(self):
            return [{
                "name": "sample-project",
                "description": "A sample project",
                "html_url": "https://github.com/octocat/sample-project",
                "language": "Python",
                "topics": ["fastapi"],
                "stargazers_count": 12,
                "fork": False,
            }]

    class MockClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url, params):
            assert url == "https://api.github.com/users/octocat/repos"
            assert params["per_page"] == 100
            return MockResponse()

    monkeypatch.setattr("app.routers.profiles.httpx.AsyncClient", MockClient)
    resp = await client.post(
        "/api/v1/profiles/github/repos",
        headers=auth_headers,
        json={"github_username": "octocat"},
    )
    assert resp.status_code == 200
    assert resp.json()["repositories"][0]["name"] == "sample-project"
    assert resp.json()["repositories"][0]["topics"] == ["fastapi"]
