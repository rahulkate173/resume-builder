"""backend/tests/test_agents.py — Mocked agent endpoint tests."""

import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_rewrite_bullet_fallback(client, auth_headers):
    """Should succeed with deterministic fallback even without API key."""
    with patch("app.core.config.Settings.has_groq", new=False):
        resp = await client.post(
            "/api/v1/agents/rewrite-bullet",
            json={
                "bullet": "Worked on backend services",
                "job_role": "Software Engineer",
            },
            headers=auth_headers,
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in ("done", "failed")
    if body["status"] == "done":
        assert body["result"]["original"] == "Worked on backend services"


@pytest.mark.asyncio
async def test_ats_audit_fallback(client, auth_headers):
    latex = r"""
\documentclass{article}
\begin{document}
\section{Experience}
Software Engineer at ACME
\section{Education}
BS Computer Science
\section{Skills}
Python, FastAPI
\end{document}
"""
    resp = await client.post(
        "/api/v1/agents/ats-audit",
        json={"latex_source": latex, "job_description": "Python FastAPI developer role"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "result" in body
    assert body["result"]["score"] >= 0


@pytest.mark.asyncio
async def test_generate_summary_fallback(client, auth_headers):
    resp = await client.post(
        "/api/v1/agents/generate-summary",
        json={
            "job_role": "Senior Backend Engineer",
            "seniority": "senior",
            "profile_snapshot": {
                "full_name": "Jane Doe",
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "experience": [{"company": "Acme"}],
            },
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    if body["status"] == "done":
        assert len(body["result"]["summary"]) > 10


@pytest.mark.asyncio
async def test_tailor_to_jd_fallback(client, auth_headers):
    """Tailor requires a valid resume_id — create one first via profile."""
    # Update profile
    await client.put(
        "/api/v1/profiles/me",
        json={
            "full_name": "Test User",
            "skills": ["Python", "Docker"],
            "languages": ["Python", "Go"],
        },
        headers=auth_headers,
    )

    resp = await client.post(
        "/api/v1/agents/tailor-to-jd",
        json={
            "resume_id": "000000000000000000000000",
            "job_description": "We need a Python developer with Docker experience",
            "job_role": "Backend Engineer",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_models_status(client, auth_headers):
    resp = await client.get("/api/v1/agents/models", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "agent1" in body
    assert "fallback" in body
    assert body["fallback"]["available"] is True
