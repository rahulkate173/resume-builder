"""
backend/app/core/config.py
Application settings via pydantic-settings (reads from .env automatically).
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Optional

from pydantic import field_validator, model_validator
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import (
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
)


class _RawAllowedOriginsSource:
    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name == "allowed_origins" and isinstance(value, str):
            return value
        return super().prepare_field_value(
            field_name, field, value, value_is_complex
        )


class _AllowedOriginsEnvSource(_RawAllowedOriginsSource, EnvSettingsSource):
    pass


class _AllowedOriginsDotEnvSource(_RawAllowedOriginsSource, DotEnvSettingsSource):
    pass


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
        "https://resume-builder-rho-sooty.vercel.app/"
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

    # ── Gemini (LangChain model for all agents) ────────────────────────────
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"

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

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: EnvSettingsSource,
        dotenv_settings: DotEnvSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            _AllowedOriginsEnvSource(
                settings_cls,
                case_sensitive=env_settings.case_sensitive,
                env_prefix=env_settings.env_prefix,
                env_nested_delimiter=env_settings.env_nested_delimiter,
                env_ignore_empty=env_settings.env_ignore_empty,
                env_parse_none_str=env_settings.env_parse_none_str,
                env_parse_enums=env_settings.env_parse_enums,
            ),
            _AllowedOriginsDotEnvSource(
                settings_cls,
                env_file=dotenv_settings.env_file,
                env_file_encoding=dotenv_settings.env_file_encoding,
                case_sensitive=dotenv_settings.case_sensitive,
                env_prefix=dotenv_settings.env_prefix,
                env_nested_delimiter=dotenv_settings.env_nested_delimiter,
                env_ignore_empty=dotenv_settings.env_ignore_empty,
                env_parse_none_str=dotenv_settings.env_parse_none_str,
                env_parse_enums=dotenv_settings.env_parse_enums,
            ),
            file_secret_settings,
        )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | list[str]) -> list[str]:
        if not isinstance(value, str):
            return value

        value = value.strip()
        if not value:
            return []

        if value.startswith("["):
            try:
                origins = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "ALLOWED_ORIGINS must be a JSON array or comma-separated origins."
                ) from exc
            if not isinstance(origins, list):
                raise ValueError("ALLOWED_ORIGINS must be a JSON array.")
            return origins

        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def has_tavily(self) -> bool:
        return bool(self.tavily_api_key)

    @property
    def has_github(self) -> bool:
        return bool(self.github_token)

    @property
    def ai_available(self) -> bool:
        return self.has_gemini

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if not self.debug and (
            len(self.jwt_secret_key) < 32
            or self.jwt_secret_key == "change-me-in-production-supersecret-key"
        ):
            raise ValueError(
                "JWT_SECRET_KEY must be a unique secret of at least 32 characters when DEBUG is false."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
