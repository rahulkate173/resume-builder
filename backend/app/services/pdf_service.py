"""
backend/app/services/pdf_service.py
Async PDF compilation service. Mirrors legacy mcp_custom logic.
Supports: latexonline.cc (primary) → reportlab fallback (when LaTeX unavailable).
"""

from __future__ import annotations

import asyncio
import base64
import re
from typing import Optional

import httpx

from app.core.config import get_settings

settings = get_settings()


async def compile_latex_to_pdf(
    latex_source: str,
) -> tuple[bool, Optional[bytes], str]:
    """
    Compile LaTeX source to PDF bytes.
    Returns (success, pdf_bytes, error_message).
    """
    backend = settings.latex_backend.lower()

    if backend == "latexonline":
        return await _compile_latexonline(latex_source)
    elif backend == "local":
        return await _compile_local(latex_source)
    else:
        return await _compile_latexonline(latex_source)


async def _compile_latexonline(latex_source: str) -> tuple[bool, Optional[bytes], str]:
    """Compile via latexonline.cc public API."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                settings.latex_online_url,
                data={"code": latex_source},
            )
            if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("application/pdf"):
                return True, resp.content, ""
            else:
                # Some APIs return compiled file in a different way
                error_text = resp.text[:300] if resp.text else f"HTTP {resp.status_code}"
                return False, None, f"LaTeX compile failed: {error_text}"
    except httpx.TimeoutException:
        return False, None, "LaTeX compilation timed out (60s). Try again."
    except Exception as e:
        return False, None, f"LaTeX compilation error: {e}"


async def _compile_local(latex_source: str) -> tuple[bool, Optional[bytes], str]:
    """Compile LaTeX using local pdflatex installation."""
    import tempfile, os, subprocess

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        pdf_path = os.path.join(tmpdir, "resume.pdf")

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_source)

        try:
            proc = await asyncio.create_subprocess_exec(
                "pdflatex",
                "-interaction=nonstopmode",
                "-output-directory", tmpdir,
                tex_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tmpdir,
            )
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)

            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    return True, f.read(), ""
            else:
                err = stderr.decode(errors="ignore")[:500]
                return False, None, f"pdflatex failed: {err}"
        except FileNotFoundError:
            return False, None, "pdflatex not found. Install TeX Live or set LATEX_BACKEND=latexonline"
        except asyncio.TimeoutError:
            return False, None, "pdflatex timed out."
        except Exception as e:
            return False, None, str(e)


def validate_latex(latex_source: str) -> tuple[bool, list[str]]:
    """
    Quick structural validation of LaTeX source.
    Returns (is_valid, list_of_issues).
    """
    issues = []

    if "\\begin{document}" not in latex_source:
        issues.append("Missing \\begin{document}")
    if "\\end{document}" not in latex_source:
        issues.append("Missing \\end{document}")
    if "\\documentclass" not in latex_source:
        issues.append("Missing \\documentclass declaration")

    # Check balanced braces
    depth = 0
    for ch in latex_source:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if depth < 0:
            issues.append("Unbalanced braces detected (extra closing brace)")
            break
    if depth > 0:
        issues.append(f"Unbalanced braces detected ({depth} unclosed)")

    # Check for placeholder tokens (unfilled)
    unfilled = re.findall(r"\{\{[A-Z_]+\}\}", latex_source)
    if unfilled:
        issues.append(f"Unfilled placeholder tokens: {', '.join(set(unfilled))}")

    return len(issues) == 0, issues
