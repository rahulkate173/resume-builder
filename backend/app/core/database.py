"""
backend/app/core/database.py
Async MongoDB connection via Motor with lifespan management.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_client() -> AsyncIOMotorClient:
    if _client is None:
        raise RuntimeError("Database not initialised — call startup() first.")
    return _client


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not initialised — call startup() first.")
    return _db


async def startup() -> None:
    """Open connection pool."""
    global _client, _db
    _client = AsyncIOMotorClient(
        settings.mongodb_uri,
        maxPoolSize=settings.mongodb_max_pool_size,
        minPoolSize=settings.mongodb_min_pool_size,
        serverSelectionTimeoutMS=5000,
    )
    _db = _client[settings.mongodb_db_name]
    await _ensure_indexes()


async def shutdown() -> None:
    """Close connection pool."""
    global _client, _db
    if _client:
        _client.close()
    _client = None
    _db = None


async def _ensure_indexes() -> None:
    """Create necessary MongoDB indexes."""
    db = get_db()
    # users
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
    # profiles
    await db.profiles.create_index("user_id", unique=True)
    # resumes (history)
    await db.resumes.create_index("user_id")
    await db.resumes.create_index([("user_id", 1), ("created_at", -1)])
    # agent_runs
    await db.agent_runs.create_index("user_id")
    await db.agent_runs.create_index([("user_id", 1), ("created_at", -1)])


async def ping() -> bool:
    """Return True if MongoDB is reachable."""
    try:
        await get_client().admin.command("ping")
        return True
    except Exception:
        return False
