"""
backend/app/core/config.py
Application settings via pydantic-settings (reads from .env automatically).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ─────────────────────────────────────────────────────────────────
    app_name: str = "AI Resume Builder"
    app_version: str = "2.0.0"
    debug: bool = False
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:80",
    ]

    # ── MongoDB ──────────────────────────────────────────────────────────────
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "resume_builder"
    mongodb_max_pool_size: int = 20
    mongodb_min_pool_size: int = 5

    # ── JWT ──────────────────────────────────────────────────────────────────
    jwt_secret_key: str = "change-me-in-production-supersecret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24 hours
    jwt_refresh_expire_days: int = 7

    # ── Groq (single LLM provider for all agents) ─────────────────────────
    groq_api_key: Optional[str] = None
    groq_model:   str = "qwen/qwen3.8-27b"
    # backwards-compat aliases
    agent1_model: str = "qwen/qwen3.8-27b"

    # ── Tavily (Web Search Agent) ─────────────────────────────────────────
    tavily_api_key: Optional[str] = None

    # ── GitHub (Repo Fetch Agent) ─────────────────────────────────────────
    github_token: Optional[str] = None

    # ── PDF / LaTeX backend ────────────────────────────────────────────────
    latex_backend: str = "latexonline"
    latex_online_url: str = "https://latexonline.cc/compile"

    # ── Rate limiting ─────────────────────────────────────────────────────
    rate_limit_per_minute: int = 60
    ai_rate_limit_per_minute: int = 10

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def has_tavily(self) -> bool:
        return bool(self.tavily_api_key)

    @property
    def has_github(self) -> bool:
        return bool(self.github_token)

    @property
    def ai_available(self) -> bool:
        return self.has_groq

    def groq_client(self):
        """Return a configured AsyncGroq client."""
        from groq import AsyncGroq
        return AsyncGroq(api_key=self.groq_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
