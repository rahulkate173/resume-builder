# AI Resume Builder 📄

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red.svg)](https://streamlit.io)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.x-green.svg)](https://mongodb.com)

An intelligent, multi-agent resume builder that generates **ATS-optimised, one-page LaTeX resumes** tailored to any job description — powered by a 3-agent AI pipeline with PDF output via Model Context Protocol (MCP).

---

## ✨ Features

| Feature | Details |
|---|---|
| 🤖 **Multi-Agent Pipeline** | Agent 1 generates, Agent 2 verifies & loops, LLM 3 polishes |
| 🎯 **JD-Tailored Resumes** | Keywords matched, experience curated per job description |
| 📎 **MCP PDF Generation** | LaTeX → PDF via FastMCP server (latexonline / local pdflatex) |
| 👤 **Internal Profile** | Enter details once; reused for every resume |
| 🔐 **Auth + MongoDB** | Secure login with JWT, all data in MongoDB |
| 🎨 **3 LaTeX Templates** | Classic, Modern, Minimal (or AI auto-picks) |
| 📚 **History** | Browse, download LaTeX and PDF from past runs |
| 🌙 **Dark UI** | Glassmorphism dark-mode Streamlit interface |

---

## 🏗 Architecture

```
Job Role + JD + Company ─┐
Internal Profile ─────────┤
Template ─────────────────┤
                          ▼
                    ┌─────────────┐
                    │  Agent 1    │  ← Grok / Qwen  (via Groq API)
                    │ [Generator] │    Selects template, generates LaTeX
                    └──────┬──────┘
                           │  (loop up to 3×)
                           ▼
                    ┌─────────────┐
                    │  Agent 2    │  ← GPT OSS 120B (via OpenRouter)
                    │ [Verifier]  │    Checks: LaTeX valid? JD match?
                    └──────┬──────┘    Experience relevant? One page?
                     ✅pass│ ❌fail → feedback → Agent 1
                           ▼
                    Final curated LaTeX (ONE page)
                           │
                           ▼
                    ┌─────────────┐
                    │   LLM 3     │  ← Mistral Small
                    │  [Polisher] │    Final formatting fix
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  MCP Tool   │  ← FastMCP server
                    │ [PDF Build] │    latexonline.cc / pdflatex
                    └──────┬──────┘
                           ▼
                    ✅ final_resume.pdf
```

---

## 📦 Project Structure

```
resume-builder/
├── app.py                          # Streamlit main entry point
├── requirements.txt
├── .env.example                    # Environment variables template
├── .streamlit/
│   └── config.toml                 # Streamlit theme & server config
│
├── config/
│   └── settings.py                 # Pydantic settings (all config in one place)
│
├── auth/
│   └── auth.py                     # bcrypt + JWT auth, profile CRUD
│
├── database/
│   ├── connection.py               # PyMongo connection pool
│   └── models.py                   # Pydantic document models
│
├── agents/
│   ├── agent1_generator.py         # Agent 1 — Groq (Grok/Qwen)
│   ├── agent2_verifier.py          # Agent 2 — GPT OSS 120B (OpenRouter)
│   ├── llm3_compiler.py            # LLM 3 — Mistral Small
│   └── pipeline.py                 # Orchestrator (runs the full loop)
│
├── mcp/
│   ├── latex_pdf_server.py         # FastMCP server with PDF tools
│   └── mcp_client.py               # In-process client wrapper
│
├── templates/
│   ├── template_classic.py         # Classic professional LaTeX skeleton
│   ├── template_modern.py          # Modern two-column skeleton
│   └── template_minimal.py         # Minimal ATS-friendly skeleton
│
├── pages/
│   ├── 1_🔐_Login.py
│   ├── 2_👤_Profile.py             # Internal details (stored once)
│   ├── 3_📝_Generate_Resume.py     # Main generation page
│   ├── 4_📚_History.py             # Resume history
│   └── 5_⚙️_Settings.py
│
└── utils/
    └── ui_helpers.py               # CSS design system & UI components
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.11+**
- **MongoDB** running locally (`mongodb://localhost:27017`) or a MongoDB Atlas URI
- (Optional) **pdflatex** on PATH for local PDF compilation — otherwise uses `latexonline.cc`

### 2. Clone & Install

```bash
git clone https://github.com/your-org/resume-builder.git
cd resume-builder
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure `.env`

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=resume_builder

JWT_SECRET_KEY=some-random-secret-32-chars

# Agent 1 — Groq (supports Llama/Qwen/Gemma models)
GROQ_API_KEY=gsk_...
AGENT1_MODEL=llama-3.3-70b-versatile

# Agent 2 — OpenRouter (GPT OSS 120B class)
OPENROUTER_API_KEY=sk-or-...
AGENT2_MODEL=meta-llama/llama-3.1-405b-instruct

# LLM 3 — Mistral AI
MISTRALAI_API_KEY=...
LLM3_MODEL=mistral-small-latest

# LaTeX backend: "latexonline" (no install) or "local" (pdflatex required)
LATEX_BACKEND=latexonline
```

### 4. Run

```bash
streamlit run app.py
```

Visit **http://localhost:8501** → Register → Fill Profile → Generate!

---

## 🔑 API Keys

| Key | Where to get it | Used by |
|---|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | Agent 1 |
| `OPENROUTER_API_KEY` | [openrouter.ai/keys](https://openrouter.ai/keys) | Agent 2 |
| `MISTRALAI_API_KEY` | [console.mistral.ai](https://console.mistral.ai) | LLM 3 |

---

## 🤖 Agent Models

| Agent | Default Model | Provider | Notes |
|---|---|---|---|
| Agent 1 | `llama-3.3-70b-versatile` | Groq | Change to `qwen-qwq-32b` or any Groq model |
| Agent 2 | `meta-llama/llama-3.1-405b-instruct` | OpenRouter | 405B = ~120B active params (MoE) |
| LLM 3 | `mistral-small-latest` | Mistral AI | Final polish & compilation |

---

## 📎 MCP Server

The MCP server (`mcp/latex_pdf_server.py`) exposes two tools:

| Tool | Description |
|---|---|
| `generate_pdf_from_latex` | Compiles LaTeX → PDF (latexonline or local pdflatex) |
| `validate_latex_syntax` | Quick structural check of LaTeX source |

Run standalone:
```bash
python mcp/latex_pdf_server.py
```

---

## 👤 Internal Profile Fields

Stored **once** at registration, editable anytime from the Profile page:

- **Personal**: name, email, phone, location
- **Online**: LinkedIn, GitHub, LeetCode, Codeforces, portfolio, Kaggle, Twitter, custom links
- **Professional Summary**
- **Experience**: company, role, duration, location, bullet points
- **Education**: institution, degree, field, GPA, duration
- **Projects**: name, tech stack, duration, link, bullets
- **Certifications & Achievements**
- **Skills & Languages**

---

## 🗄 MongoDB Collections

| Collection | Purpose |
|---|---|
| `users` | Auth credentials |
| `profiles` | Internal profile details |
| `history` | Resume generation history (LaTeX + PDF) |

---

## 🤝 Contributing

See [CONTRIBUTE.md](CONTRIBUTE.md).

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.
