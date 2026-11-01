from __future__ import annotations

import re
from textwrap import dedent
from typing import Any

from groq import Groq

from config.settings import get_settings
from mcp_custom.mcp_client import compile_latex_to_pdf, check_latex_valid

settings = get_settings()

_SYSTEM_PROMPT = dedent("""\
You are a LaTeX expert and resume formatter.

Your task: receive a nearly-complete LaTeX resume and perform FINAL polish.

Instructions:
1. Fix any LaTeX syntax errors or compilation warnings you can spot.
2. Ensure the document will fit on exactly ONE page — tighten margins, reduce font size,
   shorten bullets if needed (stay truthful, just condense phrasing).
3. Make sure all special characters are escaped: %, &, #, _, $, ^.
4. Do NOT change the substance — only fix formatting and length.
5. Output ONLY the final LaTeX source. No markdown fences, no explanations.
""")


def run_llm3_and_compile(
    latex_source: str,
    job_role: str = "",
) -> dict[str, Any]:
    """
    Polish the LaTeX with Groq, then compile to PDF via MCP.

    Returns:
        {
          "final_latex": str,
          "pdf_bytes": bytes | None,
          "pdf_success": bool,
          "pdf_error": str,
          "polish_applied": bool,
        }
    """
    valid, issues = check_latex_valid(latex_source)
    if not valid:
        latex_source = _polish_with_groq(latex_source, force_fix=True)

    polished = _polish_with_groq(latex_source)
    polish_applied = polished != latex_source

    pdf_success, pdf_bytes, pdf_error = compile_latex_to_pdf(polished)

    if not pdf_success and polish_applied:
        pdf_success, pdf_bytes, pdf_error = compile_latex_to_pdf(latex_source)
        if pdf_success:
            polished = latex_source

    return {
        "final_latex": polished,
        "pdf_bytes": pdf_bytes,
        "pdf_success": pdf_success,
        "pdf_error": pdf_error,
        "polish_applied": polish_applied,
    }


def _polish_with_groq(latex_source: str, force_fix: bool = False) -> str:
    """Call the Groq chat-completions API to polish the LaTeX."""
    client = Groq(api_key=settings.groq_api_key)

    extra = " Also FIX the structural LaTeX errors listed in the source." if force_fix else ""
    prompt = dedent(f"""\
Perform final polish on this LaTeX resume.{extra}

```latex
{latex_source}
""")