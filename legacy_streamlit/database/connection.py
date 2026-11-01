"""
database/connection.py
MongoDB connection pool using PyMongo (synchronous).
"""

from __future__ import annotations

from functools import lru_cache
from pymongo import MongoClient
from pymongo.database import Database
from config.settings import get_settings


@lru_cache(maxsize=1)
def _get_client() -> MongoClient:
    settings = get_settings()
    return MongoClient(settings.mongodb_uri)


def get_db() -> Database:
    settings = get_settings()
    return _get_client()[settings.mongodb_db_name]


def ping_db() -> bool:
    """Return True if MongoDB is reachable."""
    try:
        _get_client().admin.command("ping")
        return True
    except Exception:
        return False
