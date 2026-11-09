"""Tests for deployment-sensitive backend settings."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_settings_require_a_strong_jwt_secret():
    settings = Settings(debug=False, jwt_secret_key="s" * 48)

    assert settings.jwt_secret_key == "s" * 48


@pytest.mark.parametrize(
    "secret",
    ["short", "change-me-in-production-supersecret-key"],
)
def test_production_settings_reject_weak_jwt_secrets(secret):
    with pytest.raises(ValidationError, match="JWT_SECRET_KEY"):
        Settings(debug=False, jwt_secret_key=secret)
