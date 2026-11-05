"""
backend/tests/conftest.py
Shared pytest fixtures.
"""

from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator
import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Set test env before importing app
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DB_NAME", "resume_builder_test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("DEBUG", "true")

from app.main import app
from app.core.database import startup, shutdown, get_db

from app.main import app
from app.core.database import get_db# forcing it in one loop 



@pytest_asyncio.fixture(scope="session")
async def db_setup():
    await startup()
    
    # Get the active database instance inside the session loop
    database = get_db()
    
    yield
    
    # Clean up test DB using the proper database instance
    await database.users.drop()
    await database.profiles.drop()
    await database.resumes.drop()
    await database.agent_runs.drop()
    await shutdown()

@pytest_asyncio.fixture
async def client(db_setup) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict:
    """Register a test user and return Bearer auth headers."""
    reg_resp = await client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
    })
    # May already exist — try login instead
    if reg_resp.status_code not in (200, 201):
        login_resp = await client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "TestPass123!",
        })
        token = login_resp.json()["access_token"]
    else:
        token = reg_resp.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
