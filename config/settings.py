"""
config/settings.py
Centralised application settings loaded from environment / .env file.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── MongoDB ──────────────────────────────────────────────────────────────
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "resume_builder"

    # ── JWT ──────────────────────────────────────────────────────────────────
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # ── Agent 1 (Grok / Qwen via Groq) ───────────────────────────────────────
    groq_api_key: str = ""
    agent1_model: str = "llama-3.3-70b-versatile"

    # ── Agent 2 (OSS 120B via OpenRouter) ────────────────────────────────────
    openrouter_api_key: str = ""
    agent2_model: str = "meta-llama/llama-3.1-405b-instruct"

    # ── LLM 3 (Mistral Small) ────────────────────────────────────────────────
    mistralai_api_key: str = ""
    llm3_model: str = "mistral-small-latest"

    # ── LangSmith ────────────────────────────────────────────────────────────
    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_project: str = "resume-builder"

    # ── LaTeX MCP backend ────────────────────────────────────────────────────
    latex_backend: str = "latexonline"          # "local" | "latexonline"
    latex_online_url: str = "https://latexonline.cc/compile"

    # ── App ──────────────────────────────────────────────────────────────────
    app_name: str = "AI Resume Builder"
    app_version: str = "1.0.0"
    debug: bool = False

    def configure_langsmith(self) -> None:
        """Push LangSmith env vars so LangChain picks them up."""
        if self.langsmith_tracing and self.langsmith_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = self.langsmith_api_key
            os.environ["LANGCHAIN_ENDPOINT"] = self.langsmith_endpoint
            os.environ["LANGCHAIN_PROJECT"] = self.langsmith_project


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()
    s.configure_langsmith()
    return s
