"""
agents/llm3_compiler.py
LLM 3 — Final LaTeX Curator & PDF Compiler
Model: Mistral Small (via Mistral AI API)

Responsibilities:
 - Take the verified LaTeX from Agent 2 pipeline
 - Final polish: fix any remaining LaTeX issues, ensure one-page compactness
 - Trigger the MCP tool to compile to PDF
 - Return the final LaTeX + PDF bytes
"""

from __future__ import annotations

import re
from textwrap import dedent
from typing import Any

from mistralai import Mistral

from config.settings import get_settings
from mcp.mcp_client import compile_latex_to_pdf, check_latex_valid

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
    Polish the LaTeX with Mistral Small, then compile to PDF via MCP.

    Returns:
        {
          "final_latex": str,
          "pdf_bytes": bytes | None,
          "pdf_success": bool,
          "pdf_error": str,
          "polish_applied": bool,
        }
    """
    # ── Step 1: Quick structural check ───────────────────────────────────────
    valid, issues = check_latex_valid(latex_source)
    if not valid:
        # Ask LLM3 to fix it first
        latex_source = _polish_with_mistral(latex_source, force_fix=True)

    # ── Step 2: Polish with Mistral Small ────────────────────────────────────
    polished = _polish_with_mistral(latex_source)
    polish_applied = polished != latex_source

    # ── Step 3: Compile PDF via MCP ──────────────────────────────────────────
    pdf_success, pdf_bytes, pdf_error = compile_latex_to_pdf(polished)

    # If compilation failed with polished, try original
    if not pdf_success and polish_applied:
        pdf_success, pdf_bytes, pdf_error = compile_latex_to_pdf(latex_source)
        if pdf_success:
            polished = latex_source  # revert to original

    return {
        "final_latex": polished,
        "pdf_bytes": pdf_bytes,
        "pdf_success": pdf_success,
        "pdf_error": pdf_error,
        "polish_applied": polish_applied,
    }


def _polish_with_mistral(latex_source: str, force_fix: bool = False) -> str:
    """Call Mistral Small to polish the LaTeX."""
    client = Mistral(api_key=settings.mistralai_api_key)

    extra = " Also FIX the structural LaTeX errors listed in the source." if force_fix else ""
    prompt = dedent(f"""\
Perform final polish on this LaTeX resume.{extra}

```latex
{latex_source}
```

Return ONLY the corrected LaTeX. No markdown, no commentary.
""")

    response = client.chat.complete(
        model=settings.llm3_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=4096,
    )

    raw = response.choices[0].message.content or latex_source
    return _strip_fences(raw)


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:latex)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()
