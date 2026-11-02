"""
backend/app/services/pdf_service.py

PDF compilation service with 3-tier fallback:
  1. latex.ytotech.com  (online, reliable)
  2. latexonline.cc     (online, secondary)
  3. reportlab          (Python-native, no external deps — always works)
"""

from __future__ import annotations

import asyncio
import io
import re
from datetime import datetime
from typing import Any, Optional

import httpx

from app.core.config import get_settings

settings = get_settings()


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

async def compile_latex_to_pdf(
    latex_source: str,
) -> tuple[bool, Optional[bytes], str]:
    """
    Compile LaTeX → PDF bytes. 3-tier fallback chain.
    Returns (success, pdf_bytes, error_message).
    """
    backend = settings.latex_backend.lower()

    if backend == "local":
        return await _compile_local(latex_source)

    # Try online services first
    ok, pdf, err = await _compile_ytotech(latex_source)
    if ok:
        return True, pdf, ""

    ok, pdf, err2 = await _compile_latexonline(latex_source)
    if ok:
        return True, pdf, ""

    # Both online services failed — use Python-native fallback
    # We can't produce a LaTeX-rendered PDF without a LaTeX engine,
    # but we can return a placeholder and let export_pdf handle it
    return False, None, f"Online LaTeX failed: ytotech={err}; latexonline={err2}"


async def generate_pdf_from_resume_doc(
    doc: dict,
    profile: dict | None = None,
) -> tuple[bool, Optional[bytes], str]:
    """
    Generate a professional PDF directly from a resume DB document + profile.
    Uses reportlab — no external services needed.
    Called as the ultimate fallback when LaTeX compilation fails.
    """
    try:
        pdf_bytes = _build_reportlab_pdf(doc, profile or {})
        return True, pdf_bytes, ""
    except Exception as e:
        return False, None, f"reportlab generation failed: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# Online LaTeX APIs
# ─────────────────────────────────────────────────────────────────────────────

async def _compile_ytotech(latex_source: str) -> tuple[bool, Optional[bytes], str]:
    """latex.ytotech.com — JSON body, returns PDF."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://latex.ytotech.com/builds/sync",
                json={
                    "compiler": "pdflatex",
                    "resources": [{"main": True, "content": latex_source}],
                },
            )
            ct = resp.headers.get("content-type", "")
            if resp.status_code == 200 and "application/pdf" in ct:
                return True, resp.content, ""
            return False, None, f"ytotech HTTP {resp.status_code}: {resp.text[:150]}"
    except httpx.TimeoutException:
        return False, None, "ytotech: timed out"
    except Exception as e:
        return False, None, f"ytotech: {e}"


async def _compile_latexonline(latex_source: str) -> tuple[bool, Optional[bytes], str]:
    """latexonline.cc — form-data POST."""
    url = getattr(settings, "latex_online_url", "https://latexonline.cc/compile")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, data={"code": latex_source})
            ct = resp.headers.get("content-type", "")
            if resp.status_code == 200 and "application/pdf" in ct:
                return True, resp.content, ""
            return False, None, f"latexonline HTTP {resp.status_code}: {resp.text[:150]}"
    except httpx.TimeoutException:
        return False, None, "latexonline: timed out"
    except Exception as e:
        return False, None, f"latexonline: {e}"


async def _compile_local(latex_source: str) -> tuple[bool, Optional[bytes], str]:
    """Local pdflatex binary."""
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        pdf_path = os.path.join(tmpdir, "resume.pdf")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_source)
        try:
            proc = await asyncio.create_subprocess_exec(
                "pdflatex", "-interaction=nonstopmode",
                "-output-directory", tmpdir, tex_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tmpdir,
            )
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    return True, f.read(), ""
            return False, None, f"pdflatex failed: {stderr.decode(errors='ignore')[:300]}"
        except FileNotFoundError:
            return False, None, "pdflatex not found"
        except asyncio.TimeoutError:
            return False, None, "pdflatex timed out"
        except Exception as e:
            return False, None, str(e)


# ─────────────────────────────────────────────────────────────────────────────
# Reportlab PDF Builder
# ─────────────────────────────────────────────────────────────────────────────

def _build_reportlab_pdf(doc: dict, profile: dict) -> bytes:
    """
    Build a clean, professional single-page resume PDF using reportlab.
    Falls back gracefully if any section is missing.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm, mm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
        Table, TableStyle, KeepTogether,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

    buffer = io.BytesIO()

    # Colours
    c_black   = HexColor("#111111")
    c_gray    = HexColor("#555555")
    c_light   = HexColor("#888888")
    c_rule    = HexColor("#222222")

    doc_obj = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    W = A4[0] - 3.6 * cm  # usable width

    # Styles
    s_name = ParagraphStyle("name", fontSize=20, leading=24, textColor=c_black,
                            fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=2)
    s_contact = ParagraphStyle("contact", fontSize=8.5, leading=12, textColor=c_gray,
                               fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4)
    s_section = ParagraphStyle("section", fontSize=9, leading=11, textColor=c_black,
                               fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=2,
                               textTransform="uppercase", tracking=1.5)
    s_body  = ParagraphStyle("body", fontSize=8.5, leading=12, textColor=c_black,
                             fontName="Helvetica")
    s_bold  = ParagraphStyle("bold", fontSize=8.5, leading=12, textColor=c_black,
                             fontName="Helvetica-Bold")
    s_italic = ParagraphStyle("italic", fontSize=8.5, leading=12, textColor=c_gray,
                              fontName="Helvetica-Oblique")
    s_bullet = ParagraphStyle("bullet", fontSize=8.5, leading=11.5, textColor=c_black,
                              fontName="Helvetica", leftIndent=12, bulletIndent=4,
                              bulletFontSize=8.5)

    def rule():
        return HRFlowable(width="100%", thickness=0.5, color=c_rule, spaceAfter=3)

    def section(title: str):
        return [Paragraph(title, s_section), rule()]

    def bullet(text: str):
        return Paragraph(f"• {text}", s_bullet)

    # ── Pull data ────────────────────────────────────────────────────────────
    name      = profile.get("full_name")  or doc.get("title", "Resume")
    email     = profile.get("email", "")
    phone     = profile.get("phone", "")
    linkedin  = profile.get("linkedin", "")
    github    = profile.get("github", "")
    location  = profile.get("location", "")
    summary   = profile.get("professional_summary", "") or doc.get("summary_used", "")
    education = profile.get("education", [])
    experience = profile.get("experience", [])
    projects  = profile.get("projects", [])
    skills    = profile.get("skills", [])
    languages = profile.get("languages", [])
    job_role  = doc.get("job_role", "")
    company   = doc.get("company", "")

    story = []

    # ── Header ───────────────────────────────────────────────────────────────
    story.append(Paragraph(name, s_name))

    contact_parts = [p for p in [phone, email, linkedin, github, location] if p]
    if contact_parts:
        story.append(Paragraph("  ·  ".join(contact_parts), s_contact))

    if job_role and company:
        story.append(Paragraph(f"Applying for: <b>{job_role}</b> @ <b>{company}</b>", s_contact))

    story.append(Spacer(1, 3))
    story.append(HRFlowable(width="100%", thickness=1.0, color=c_black, spaceAfter=4))

    # ── Summary ──────────────────────────────────────────────────────────────
    if summary:
        story += section("Professional Summary")
        story.append(Paragraph(summary[:600], ParagraphStyle(
            "summ", fontSize=8.5, leading=12.5, textColor=c_black,
            fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=4
        )))

    # ── Education ────────────────────────────────────────────────────────────
    if education:
        story += section("Education")
        for e in education:
            inst   = e.get("institution", "")
            degree = e.get("degree", "")
            field  = e.get("field", "")
            dur    = e.get("duration", "")
            gpa    = e.get("gpa", "")
            deg_str = " in ".join(filter(None, [degree, field]))
            gpa_str = f" — GPA: {gpa}" if gpa else ""
            row = Table(
                [[Paragraph(inst, s_bold), Paragraph(dur, ParagraphStyle(
                    "r", fontSize=8.5, leading=12, fontName="Helvetica",
                    textColor=c_gray, alignment=2))]],  # TA_RIGHT=2
                colWidths=[W * 0.72, W * 0.28],
            )
            row.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"),
                                      ("LEFTPADDING", (0,0), (-1,-1), 0),
                                      ("RIGHTPADDING", (0,0), (-1,-1), 0),
                                      ("TOPPADDING", (0,0), (-1,-1), 0),
                                      ("BOTTOMPADDING", (0,0), (-1,-1), 1)]))
            story.append(row)
            if deg_str or gpa_str:
                story.append(Paragraph(f"<i>{deg_str}{gpa_str}</i>", s_italic))
            story.append(Spacer(1, 3))

    # ── Experience ───────────────────────────────────────────────────────────
    if experience:
        story += section("Experience")
        for e in experience:
            co   = e.get("company", "")
            role = e.get("role", "")
            loc  = e.get("location", "")
            dur  = e.get("duration", "")
            bullets = e.get("bullets", [])

            row = Table(
                [[Paragraph(co, s_bold),
                  Paragraph(dur, ParagraphStyle("r2", fontSize=8.5, leading=12,
                                                fontName="Helvetica", textColor=c_gray, alignment=2))]],
                colWidths=[W * 0.72, W * 0.28],
            )
            row.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"),
                                      ("LEFTPADDING", (0,0), (-1,-1), 0),
                                      ("RIGHTPADDING", (0,0), (-1,-1), 0),
                                      ("TOPPADDING", (0,0), (-1,-1), 0),
                                      ("BOTTOMPADDING", (0,0), (-1,-1), 0)]))
            story.append(row)
            loc_str = f"{role}{', ' + loc if loc else ''}"
            story.append(Paragraph(f"<i>{loc_str}</i>", s_italic))
            for b in bullets[:5]:
                story.append(bullet(b))
            story.append(Spacer(1, 4))

    # ── Projects ─────────────────────────────────────────────────────────────
    if projects:
        story += section("Projects")
        for p in projects[:4]:
            pname = p.get("name", "")
            tech  = p.get("tech_stack", "")
            dur   = p.get("duration", "")
            buls  = p.get("bullets", [])
            hdr = f"<b>{pname}</b>" + (f"  <font color='#888888' size='8'>{tech}</font>" if tech else "")
            story.append(Paragraph(hdr, s_body))
            for b in buls[:3]:
                story.append(bullet(b))
            story.append(Spacer(1, 3))

    # ── Skills & Languages ───────────────────────────────────────────────────
    if skills or languages:
        story += section("Technical Skills")
        if skills:
            story.append(Paragraph(f"<b>Skills:</b> {', '.join(skills[:20])}", s_body))
        if languages:
            story.append(Paragraph(f"<b>Languages:</b> {', '.join(languages[:10])}", s_body))

    doc_obj.build(story)
    buffer.seek(0)
    return buffer.read()


# ─────────────────────────────────────────────────────────────────────────────
# LaTeX Validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_latex(latex_source: str) -> tuple[bool, list[str]]:
    issues = []
    if "\\begin{document}" not in latex_source:
        issues.append("Missing \\begin{document}")
    if "\\end{document}" not in latex_source:
        issues.append("Missing \\end{document}")
    if "\\documentclass" not in latex_source:
        issues.append("Missing \\documentclass declaration")
    depth = 0
    for ch in latex_source:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if depth < 0:
            issues.append("Unbalanced braces (extra closing brace)")
            break
    if depth > 0:
        issues.append(f"Unbalanced braces ({depth} unclosed)")
    unfilled = re.findall(r"\{\{[A-Z_]+\}\}", latex_source)
    if unfilled:
        issues.append(f"Unfilled placeholders: {', '.join(set(unfilled))}")
    return len(issues) == 0, issues
