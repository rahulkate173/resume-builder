"""
templates/__init__.py
Built-in LaTeX resume templates.
Each template is a callable that receives a `context` dict and returns a LaTeX string.
"""

from templates.template_classic import CLASSIC_TEMPLATE
from templates.template_modern import MODERN_TEMPLATE
from templates.template_minimal import MINIMAL_TEMPLATE

BUILTIN_TEMPLATES: dict[str, dict] = {
    "classic": {
        "name": "Classic",
        "description": "Traditional academic style with clear section dividers.",
        "preview_color": "#2c3e50",
        "template": CLASSIC_TEMPLATE,
    },
    "modern": {
        "name": "Modern",
        "description": "Two-column layout with a colored sidebar — great for tech roles.",
        "preview_color": "#1a73e8",
        "template": MODERN_TEMPLATE,
    },
    "minimal": {
        "name": "Minimal",
        "description": "Clean single-column, ATS-friendly, lots of whitespace.",
        "preview_color": "#34a853",
        "template": MINIMAL_TEMPLATE,
    },
}


def get_template_names() -> list[str]:
    return list(BUILTIN_TEMPLATES.keys())


def get_template(key: str) -> str:
    return BUILTIN_TEMPLATES[key]["template"]


def get_template_info(key: str) -> dict:
    return BUILTIN_TEMPLATES[key]
