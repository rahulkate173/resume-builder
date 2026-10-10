"""templates/template_minimal.py — Minimal ATS-friendly LaTeX template."""

MINIMAL_TEMPLATE = r"""
%% ──────────────────────────────────────────────────────────────────────────────
%%  MINIMAL RESUME TEMPLATE  (ATS-friendly, clean single-column)
%% ──────────────────────────────────────────────────────────────────────────────
\documentclass[11pt,letterpaper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[margin=0.65in]{geometry}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{titlesec}
\usepackage{microtype}
\usepackage{lmodern}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}

\titleformat{\section}{\normalsize\bfseries\uppercase}{}{0em}{}[\rule{\linewidth}{0.4pt}]
\titlespacing{\section}{0pt}{8pt}{4pt}

%% ════════════════════════════════════════════════════════════════════════════
\begin{document}

%% ── HEADER ────────────────────────────────────────────────────────────────
\begin{center}
{\LARGE\textbf{{{NAME}}}}\\[3pt]
{{PHONE}} \textbullet\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \textbullet\
\href{{{LINKEDIN}}}{LinkedIn} \textbullet\ \href{{{GITHUB}}}{GitHub}
{{EXTRA_LINKS_PLAIN}}
\end{center}

%% ── EDUCATION ─────────────────────────────────────────────────────────────
\section{Education}
{{EDUCATION_ENTRIES}}

%% ── EXPERIENCE ────────────────────────────────────────────────────────────
\section{Experience}
{{EXPERIENCE_ENTRIES}}

%% ── PROJECTS ──────────────────────────────────────────────────────────────
\section{Projects}
{{PROJECT_ENTRIES}}

%% ── SKILLS ────────────────────────────────────────────────────────────────
\section{Skills}
\textbf{Technical Skills:} {{SKILLS}}\\
\textbf{Languages:} {{LANGUAGES}}

%% ── ACHIEVEMENTS ──────────────────────────────────────────────────────────
{{ACHIEVEMENTS_SECTION}}

%% ── COMPETITIVE PROGRAMMING ───────────────────────────────────────────────
{{COMPETITIVE_SECTION}}

\end{document}
"""
