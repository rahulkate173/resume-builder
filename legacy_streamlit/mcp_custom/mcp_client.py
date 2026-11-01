"""
mcp/mcp_client.py
Thin Python client that calls the MCP server tools directly
(in-process, without stdio transport) for use inside Streamlit.
"""

from __future__ import annotations

import base64
from typing import Optional

# Import the functions directly from the server module
from mcp_custom.latex_pdf_server import generate_pdf_from_latex, validate_latex_syntax


def compile_latex_to_pdf(
    latex_source: str,
    backend: str = "",
) -> tuple[bool, Optional[bytes], str]:
    result = generate_pdf_from_latex(
        latex_source=latex_source,
        backend=backend,
    )

    if not result.get("success"):
        return False, None, result.get("error", "Unknown compilation error")

    pdf_base64 = result.get("pdf_base64")
    if not pdf_base64:
        return False, None, "Compiler reported success but returned no PDF data"

    try:
        pdf_bytes = base64.b64decode(pdf_base64, validate=True)
    except Exception as exc:
        return False, None, f"Invalid PDF data returned by compiler: {exc}"

    return True, pdf_bytes, ""


def check_latex_valid(latex_source: str) -> tuple[bool, list[str]]:
    """Quick structural validation of LaTeX source."""
    result = validate_latex_syntax(latex_source=latex_source)
    return result["valid"], result.get("issues", [])
