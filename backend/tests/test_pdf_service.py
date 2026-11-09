"""Tests for the online PDF compilation service."""

from unittest.mock import patch

import httpx
import pytest

from app.services.pdf_service import _compile_latexonline, _compile_ytotech


class _MockAsyncClient:
    def __init__(self, response: httpx.Response):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def post(self, *_args, **_kwargs):
        return self.response


@pytest.mark.asyncio
@pytest.mark.parametrize("compiler", [_compile_ytotech, _compile_latexonline])
async def test_online_compiler_accepts_created_pdf_response(compiler):
    pdf_bytes = b"%PDF-1.7\ncompiled PDF"
    response = httpx.Response(
        201,
        content=pdf_bytes,
        headers={"content-type": "application/pdf"},
    )

    with patch(
        "app.services.pdf_service.httpx.AsyncClient",
        return_value=_MockAsyncClient(response),
    ):
        success, result, error = await compiler("\\documentclass{article}")

    assert success is True
    assert result == pdf_bytes
    assert error == ""


@pytest.mark.asyncio
async def test_online_compiler_rejects_non_pdf_success_response():
    response = httpx.Response(
        201,
        content=b"Compilation job accepted, but PDF is not ready",
        headers={"content-type": "text/plain"},
    )

    with patch(
        "app.services.pdf_service.httpx.AsyncClient",
        return_value=_MockAsyncClient(response),
    ):
        success, result, error = await _compile_ytotech("\\documentclass{article}")

    assert success is False
    assert result is None
    assert "HTTP 201" in error
