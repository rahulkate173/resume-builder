"""
mcp/latex_pdf_server.py
FastMCP server exposing a `generate_pdf_from_latex` tool.

Backends supported:
  - "latexonline"  → https://latexonline.cc/compile  (no install needed)
  - "local"        → pdflatex must be installed on PATH
"""

from __future__ import annotations

import base64
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Annotated

import httpx
from fastmcp import FastMCP

from config.settings import get_settings

settings = get_settings()

mcp = FastMCP(
    name="latex-pdf-generator",
    version="1.0.0",
    description=(
        "MCP server for compiling LaTeX source code to PDF. "
        "Supports latexonline.cc backend and local pdflatex."
    ),
)


# ── Tool 1: generate_pdf_from_latex ──────────────────────────────────────────

@mcp.tool()
def generate_pdf_from_latex(
    latex_source: Annotated[str, "Complete LaTeX source code to compile"],
    backend: Annotated[str, "Backend to use: 'latexonline' or 'local'"] = "",
) -> dict:
    """
    Compile a LaTeX document to PDF.

    Returns a dict with:
      - success: bool
      - pdf_base64: str  (base64-encoded PDF bytes, only if success=True)
      - error: str       (error message, only if success=False)
      - backend_used: str
    """
    chosen = (backend or settings.latex_backend).lower()

    if chosen == "local":
        return _compile_local(latex_source)
    elif chosen == "latexonline":
        return _compile_latexonline(latex_source)
    else:
        return {"success": False, "error": f"Unknown backend: {chosen}"}


# ── Tool 2: validate_latex_syntax ────────────────────────────────────────────

@mcp.tool()
def validate_latex_syntax(
    latex_source: Annotated[str, "LaTeX source to validate"],
) -> dict:
    """
    Perform a quick structural check of a LaTeX document.
    Returns {'valid': bool, 'issues': list[str]}.
    """
    issues: list[str] = []

    if r"\begin{document}" not in latex_source:
        issues.append("Missing \\begin{document}")
    if r"\end{document}" not in latex_source:
        issues.append("Missing \\end{document}")
    if r"\documentclass" not in latex_source:
        issues.append("Missing \\documentclass declaration")

    # Count matching braces
    opens = latex_source.count("{")
    closes = latex_source.count("}")
    if opens != closes:
        issues.append(f"Unbalanced braces: {opens} opens vs {closes} closes")

    return {"valid": len(issues) == 0, "issues": issues}


# ── Backend implementations ───────────────────────────────────────────────────

def _compile_latexonline(latex_source: str) -> dict:
    """Call latexonline.cc REST API."""
    url = settings.latex_online_url  # e.g. https://latexonline.cc/compile
    try:
        resp = httpx.post(
            url,
            content=latex_source.encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            params={"command": "pdflatex"},
            timeout=60.0,
        )
        if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("application/pdf"):
            return {
                "success": True,
                "pdf_base64": base64.b64encode(resp.content).decode(),
                "backend_used": "latexonline",
            }
        else:
            return {
                "success": False,
                "error": f"latexonline returned HTTP {resp.status_code}: {resp.text[:500]}",
                "backend_used": "latexonline",
            }
    except Exception as exc:
        return {"success": False, "error": str(exc), "backend_used": "latexonline"}


def _compile_local(latex_source: str) -> dict:
    """Compile using local pdflatex (must be on PATH)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / "resume.tex"
        pdf_path = Path(tmpdir) / "resume.pdf"
        tex_path.write_text(latex_source, encoding="utf-8")
        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, str(tex_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if pdf_path.exists():
                pdf_bytes = pdf_path.read_bytes()
                return {
                    "success": True,
                    "pdf_base64": base64.b64encode(pdf_bytes).decode(),
                    "backend_used": "local",
                }
            else:
                return {
                    "success": False,
                    "error": result.stdout[-2000:] + result.stderr[-1000:],
                    "backend_used": "local",
                }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "pdflatex not found. Install TeX Live or MiKTeX.",
                "backend_used": "local",
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "pdflatex timed out.", "backend_used": "local"}


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
