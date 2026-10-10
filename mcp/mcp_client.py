"""
mcp/mcp_client.py
Thin Python client that calls the MCP server tools directly
(in-process, without stdio transport) for use inside Streamlit.
"""

from __future__ import annotations

import base64
from typing import Optional

# Import the functions directly from the server module
from mcp.latex_pdf_server import generate_pdf_from_latex, validate_latex_syntax


def compile_latex_to_pdf(latex_source: str, backend: str = "") -> tuple[bool, Optional[bytes], str]:
    """
    Compile LaTeX → PDF via the MCP tool.

    Returns:
        (success, pdf_bytes_or_None, error_message)
    """
    result = generate_pdf_from_latex(latex_source=latex_source, backend=backend)
    if result.get("success"):
        pdf_bytes = base64.b64decode(result["pdf_base64"])
        return True, pdf_bytes, ""
    return False, None, result.get("error", "Unknown error")


def check_latex_valid(latex_source: str) -> tuple[bool, list[str]]:
    """Quick structural validation of LaTeX source."""
    result = validate_latex_syntax(latex_source=latex_source)
    return result["valid"], result.get("issues", [])
