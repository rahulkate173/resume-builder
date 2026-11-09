"""
backend/app/services/latex_templates.py
Four production-quality LaTeX resume templates:
1. Executive Monochrome (Jake's Resume / ATS gold standard)
2. Modern Tech Minimal (monospace metadata tags)
3. Classic Serif Academic (Harvard/Ivy-style)
4. Compact Two-Column (high-density)
"""

from __future__ import annotations


# ══════════════════════════════════════════════════════════════════════════════
# Template 1: Executive Monochrome (ATS Gold Standard)
# ══════════════════════════════════════════════════════════════════════════════

EXECUTIVE_MONOCHROME = r"""
\documentclass[letterpaper,11pt]{article}

\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage[usenames,dvipsnames]{color}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\setlist[itemize]{topsep=1pt,itemsep=0pt,parsep=0pt,partopsep=0pt}
\input{glyphtounicode}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}
\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{\vspace{-4pt}\bfseries\raggedright\large}{}{0em}{}[\color{black}\titlerule\vspace{-5pt}]
\pdfgentounicode=1

\newcommand{\resumeItem}[1]{\item\small{#1\vspace{-2pt}}}
\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}
\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}
\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}
\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}
\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

\begin{center}
    \textbf{\Huge \scshape {{NAME}}} \\ \vspace{1pt}
    \small {{PHONE}} $|$
    \href{mailto:{{EMAIL}}}{\underline{{{EMAIL}}}} $|$
    \href{{{LINKEDIN}}}{\underline{LinkedIn}} $|$
    \href{{{GITHUB}}}{\underline{GitHub}}
    {{EXTRA_LINKS}}
\end{center}

\section{Education}
  \resumeSubHeadingListStart
    {{EDUCATION_ENTRIES}}
  \resumeSubHeadingListEnd

\section{Experience}
  \resumeSubHeadingListStart
    {{EXPERIENCE_ENTRIES}}
  \resumeSubHeadingListEnd

\section{Projects}
    \resumeSubHeadingListStart
      {{PROJECT_ENTRIES}}
    \resumeSubHeadingListEnd

\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Skills}{: {{SKILLS}}} \\
     \textbf{Languages}{: {{LANGUAGES}}}
    }}
 \end{itemize}

{{ACHIEVEMENTS_SECTION}}
{{COMPETITIVE_SECTION}}

\end{document}
"""


# ══════════════════════════════════════════════════════════════════════════════
# Template 2: Modern Tech Minimal
# ══════════════════════════════════════════════════════════════════════════════

MODERN_TECH_MINIMAL = r"""
\documentclass[10pt,letterpaper]{article}

\usepackage[margin=0.6in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{parskip}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{array}
\definecolor{accent}{HTML}{111111}
\definecolor{muted}{HTML}{555555}

\titleformat{\section}{\large\bfseries\color{accent}}{}{0em}{}[\vspace{-6pt}\rule{\linewidth}{0.5pt}\vspace{2pt}]
\setlist[itemize]{leftmargin=*, topsep=2pt, itemsep=1pt}

\begin{document}
\pagestyle{empty}

{\Huge\bfseries {{NAME}}} \hfill
\small\texttt{\href{mailto:{{EMAIL}}}{{{EMAIL}}}} $\cdot$
\texttt{{{PHONE}}} $\cdot$
\href{{{LINKEDIN}}}{\texttt{LinkedIn}} $\cdot$
\href{{{GITHUB}}}{\texttt{GitHub}}

\vspace{4pt}
\hrule
\vspace{6pt}

\section{Experience}
{{EXPERIENCE_ENTRIES}}

\section{Projects}
{{PROJECT_ENTRIES}}

\section{Education}
{{EDUCATION_ENTRIES}}

\section{Skills \& Technologies}
\textbf{Technical:} {{SKILLS}} \\
\textbf{Languages:} {{LANGUAGES}}

{{ACHIEVEMENTS_SECTION}}

\end{document}
"""


# ══════════════════════════════════════════════════════════════════════════════
# Template 3: Classic Serif Academic (Harvard/Ivy style)
# ══════════════════════════════════════════════════════════════════════════════

CLASSIC_SERIF_ACADEMIC = r"""
\documentclass[12pt,letterpaper]{article}

\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{mathptmx}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{titlesec}
\usepackage{parskip}

\titleformat{\section}{\large\bfseries\scshape}{}{0em}{}[\rule{\linewidth}{0.4pt}]
\setlength{\parindent}{0pt}
\setlist[itemize]{leftmargin=1.5em, topsep=2pt, itemsep=1pt}

\begin{document}
\pagestyle{empty}

\begin{center}
{\huge\scshape\bfseries {{NAME}}}\\[4pt]
{{PHONE}} $\cdot$ \href{mailto:{{EMAIL}}}{{{EMAIL}}} $\cdot$
\href{{{LINKEDIN}}}{LinkedIn} $\cdot$
\href{{{GITHUB}}}{GitHub}\\
\end{center}
\vspace{6pt}

\section{Education}
{{EDUCATION_ENTRIES}}

\section{Professional Experience}
{{EXPERIENCE_ENTRIES}}

\section{Research \& Projects}
{{PROJECT_ENTRIES}}

\section{Skills}
\textbf{Technical Skills:} {{SKILLS}} \\
\textbf{Programming Languages:} {{LANGUAGES}}

{{ACHIEVEMENTS_SECTION}}

\end{document}
"""


# ══════════════════════════════════════════════════════════════════════════════
# Template 4: Compact Two-Column (high-density for senior engineers)
# ══════════════════════════════════════════════════════════════════════════════

COMPACT_TWO_COLUMN = r"""
\documentclass[10pt,letterpaper]{article}

\usepackage[margin=0.5in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{multicol}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{titlesec}
\usepackage{xcolor}
\definecolor{sidebar}{HTML}{F5F5F5}

\titleformat{\section}{\normalsize\bfseries\uppercase}{}{0em}{}[\vspace{-4pt}\rule{\linewidth}{0.3pt}]
\setlist[itemize]{leftmargin=*, nosep, topsep=0pt}

\begin{document}
\pagestyle{empty}

% Header
\begin{center}
{\huge\bfseries {{NAME}}} \\[2pt]
\small \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad
{{PHONE}} \quad
\href{{{LINKEDIN}}}{linkedin} \quad
\href{{{GITHUB}}}{github}
\end{center}
\vspace{2pt}\hrule\vspace{4pt}

\begin{multicols}{2}

\section{Experience}
{{EXPERIENCE_ENTRIES}}

\columnbreak

\section{Skills}
\textbf{Technical:} {{SKILLS}} \\[2pt]
\textbf{Languages:} {{LANGUAGES}}

\section{Education}
{{EDUCATION_ENTRIES}}

\section{Projects}
{{PROJECT_ENTRIES}}

{{ACHIEVEMENTS_SECTION}}

\end{multicols}

\end{document}
"""


# ── Registry ──────────────────────────────────────────────────────────────────

TEMPLATES: dict[str, dict] = {
    "executive": {
        "name": "Executive Monochrome",
        "description": "ATS gold standard — single column, Jake's Resume inspired. Best for corporate & engineering roles.",
        "template": EXECUTIVE_MONOCHROME,
    },
    "modern": {
        "name": "Modern Tech Minimal",
        "description": "Clean layout with monospace metadata. Ideal for tech & startup roles.",
        "template": MODERN_TECH_MINIMAL,
    },
    "classic": {
        "name": "Classic Serif Academic",
        "description": "Traditional Harvard/Ivy-style layout. Perfect for research, academia, and finance.",
        "template": CLASSIC_SERIF_ACADEMIC,
    },
    "compact": {
        "name": "Compact Two-Column",
        "description": "High-density layout for senior engineers with extensive experience.",
        "template": COMPACT_TWO_COLUMN,
    },
}


def get_template_names() -> list[str]:
    return list(TEMPLATES.keys())


def get_template(key: str) -> str:
    return TEMPLATES.get(key, TEMPLATES["executive"])["template"]


def get_template_info(key: str) -> dict:
    return TEMPLATES.get(key, TEMPLATES["executive"])


def get_all_templates() -> dict[str, dict]:
    """Return metadata for all templates (without raw LaTeX source)."""
    return {k: {kk: vv for kk, vv in v.items() if kk != "template"}
            for k, v in TEMPLATES.items()}
