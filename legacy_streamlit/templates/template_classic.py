"""templates/template_classic.py — Classic academic/professional LaTeX template skeleton."""

CLASSIC_TEMPLATE = r"""
%% ──────────────────────────────────────────────────────────────────────────────
%%  CLASSIC RESUME TEMPLATE
%%  Designed for: traditional professional / academic roles
%% ──────────────────────────────────────────────────────────────────────────────
\documentclass[letterpaper,11pt]{article}

\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{xcolor}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
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

\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\pdfgentounicode=1

%% ── Custom commands ────────────────────────────────────────────────────────
\newcommand{\resumeItem}[1]{\item\small{#1 \vspace{-2pt}}}

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

%% ════════════════════════════════════════════════════════════════════════════
\begin{document}

%% ── HEADER ────────────────────────────────────────────────────────────────
\begin{center}
    \textbf{\Huge \scshape {{NAME}}} \\ \vspace{1pt}
    \small
    {{PHONE}} $|$
    \href{mailto:{{EMAIL}}}{\underline{{{EMAIL}}}} $|$
    \href{{{LINKEDIN}}}{\underline{LinkedIn}} $|$
    \href{{{GITHUB}}}{\underline{GitHub}}
    {{EXTRA_LINKS}}
\end{center}

%% ── EDUCATION ─────────────────────────────────────────────────────────────
\section{Education}
  \resumeSubHeadingListStart
    {{EDUCATION_ENTRIES}}
  \resumeSubHeadingListEnd

%% ── EXPERIENCE ────────────────────────────────────────────────────────────
\section{Experience}
  \resumeSubHeadingListStart
    {{EXPERIENCE_ENTRIES}}
  \resumeSubHeadingListEnd

%% ── PROJECTS ──────────────────────────────────────────────────────────────
\section{Projects}
    \resumeSubHeadingListStart
      {{PROJECT_ENTRIES}}
    \resumeSubHeadingListEnd

%% ── TECHNICAL SKILLS ──────────────────────────────────────────────────────
\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Skills}{: {{SKILLS}}} \\
     \textbf{Languages}{: {{LANGUAGES}}}
    }}
 \end{itemize}

%% ── ACHIEVEMENTS ──────────────────────────────────────────────────────────
{{ACHIEVEMENTS_SECTION}}

%% ── COMPETITIVE PROGRAMMING ───────────────────────────────────────────────
{{COMPETITIVE_SECTION}}

\end{document}
"""
