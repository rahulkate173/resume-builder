"""templates/template_modern.py — Modern two-column LaTeX template."""

MODERN_TEMPLATE = r"""
%% ──────────────────────────────────────────────────────────────────────────────
%%  MODERN RESUME TEMPLATE  (two-column with colored accent)
%% ──────────────────────────────────────────────────────────────────────────────
\documentclass[10pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[margin=0.5in, top=0.4in, bottom=0.4in]{geometry}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{multicol}
\usepackage{fontawesome5}
\usepackage{tabularx}
\usepackage{array}

\definecolor{accent}{RGB}{26,115,232}
\definecolor{lightgray}{RGB}{245,245,245}
\definecolor{darkgray}{RGB}{60,60,60}

\hypersetup{colorlinks=true,urlcolor=accent,linkcolor=accent}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{2pt}

\titleformat{\section}{\large\bfseries\color{accent}}{}{0em}{}[\color{accent}\rule{\linewidth}{1.5pt}]
\titlespacing{\section}{0pt}{6pt}{4pt}

\newcommand{\entry}[4]{%
  \textbf{#1} \hfill \textit{\small #2} \\
  \textit{\small #3} \hfill \textit{\small #4}
}

\newcommand{\projentry}[3]{%
  \textbf{#1} $|$ \textit{\small #2} \hfill \textit{\small #3}
}

%% ════════════════════════════════════════════════════════════════════════════
\begin{document}

%% ── HEADER ────────────────────────────────────────────────────────────────
{\Huge\bfseries\color{accent} {{NAME}}}\\[4pt]
\small
\faPhone\ {{PHONE}} \quad
\faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad
\faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn} \quad
\faGithub\ \href{{{GITHUB}}}{GitHub}
{{EXTRA_LINKS_ICONS}}

\rule{\linewidth}{0.4pt}

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
\section{Skills \& Technologies}
\begin{itemize}[leftmargin=*, nosep]
  \item \textbf{Technical:} {{SKILLS}}
  \item \textbf{Languages:} {{LANGUAGES}}
\end{itemize}

%% ── ACHIEVEMENTS ──────────────────────────────────────────────────────────
{{ACHIEVEMENTS_SECTION}}

%% ── COMPETITIVE PROGRAMMING ───────────────────────────────────────────────
{{COMPETITIVE_SECTION}}

\end{document}
"""
