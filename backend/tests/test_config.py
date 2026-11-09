"""Tests for deployment-sensitive backend settings."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_settings_require_a_strong_jwt_secret():
    settings = Settings(debug=False, jwt_secret_key="s" * 48)

    assert settings.jwt_secret_key == "s" * 48


@pytest.mark.parametrize(
    ("origins", "expected"),
    [
        ("https://app.example.com", ["https://app.example.com"]),
        (
            "https://app.example.com, https://admin.example.com",
            ["https://app.example.com", "https://admin.example.com"],
        ),
        (
            '["https://app.example.com", "https://admin.example.com"]',
            ["https://app.example.com", "https://admin.example.com"],
        ),
    ],
)
def test_allowed_origins_support_environment_value_formats(
    monkeypatch, origins, expected
):
    monkeypatch.setenv("ALLOWED_ORIGINS", origins)

    settings = Settings(_env_file=None, jwt_secret_key="s" * 48)

    assert settings.allowed_origins == expected


@pytest.mark.parametrize(
    "secret",
    ["short", "change-me-in-production-supersecret-key"],
)
def test_production_settings_reject_weak_jwt_secrets(secret):
    with pytest.raises(ValidationError, match="JWT_SECRET_KEY"):
        Settings(debug=False, jwt_secret_key=secret)
