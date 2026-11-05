# 🧠 AI Resume Builder v2

> Production-grade, decoupled full-stack resume builder powered by a **multi-agent AI pipeline** — FastAPI · React · MongoDB · LaTeX

[![CI/CD](https://github.com/rahulkate173/resume-builder/actions/workflows/ci.yml/badge.svg)](https://github.com/rahulkate173/resume-builder/actions/workflows/ci.yml)

---

## ✨ Features

- Decoupled FastAPI backend and React frontend.
- JWT authentication and MongoDB-backed profiles and resumes.
- Multi-agent Groq resume generation, verification, and ATS auditing.
- LaTeX templates with deterministic fallbacks when AI is unavailable.
- Docker Compose deployment and GitHub Actions CI.

---

## 🏗️ Architecture

```
resume-builder/
├── backend/                 # FastAPI (Python 3.11)
│   └── app/
│       ├── core/            # Config, DB, Security
│       ├── models/          # Pydantic v2 schemas
│       ├── routers/         # Auth, Profiles, Resumes, Agents
│       ├── agents/          # Multi-agent AI pipeline
│       └── services/        # LaTeX templates, PDF service
├── frontend/                # React 18 + Vite + TypeScript + Tailwind
│   └── src/
│       ├── api/             # Axios client with auto-refresh
│       ├── store/           # Zustand state management
│       ├── pages/           # Landing, Login, Register, Dashboard, Editor
│       ├── components/      # Navbar, FormEditor, AIAgentPanel, Templates
│       └── __tests__/       # Vitest unit tests
├── docker-compose.yml       # Production Docker stack
├── run.bat / run.sh         # One-command dev startup
└── .github/workflows/ci.yml # GitHub Actions CI/CD
```

---

## 🤖 Multi-Agent AI Pipeline

```
User input (JD + Profile)
        ↓
  Template Selector          ← auto-selects best template
        ↓
  Agent 1 — Generator        ← Groq llama-3.3-70b
        ↓
  Agent 2 — Verifier  ←──── Loop up to 3× until score ≥ 80/100
  (Groq llama-3.3-70b)
        ↓
  PDF Compiler               ← latexonline.cc / local pdflatex
        ↓
  MongoDB persist            ← cache LaTeX + PDF
```

**Deterministic fallbacks** guarantee the app works without any API keys.

---

## 🚀 Quick Start

### Option A — One command (recommended)

**Windows:**
```bat
run.bat
```

**macOS / Linux:**
```bash
chmod +x run.sh && ./run.sh
```

This automatically:
- Creates a Python virtual environment
- Installs all backend + frontend dependencies
- Copies `.env.example` → `.env`
- Starts both servers concurrently

### Option B — Manual

**Backend:**
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix:    source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Add your API keys
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**URLs:**
| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## 🐳 Docker Compose (Production)

```bash
# Copy and configure env
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Start full stack
docker compose up --build

# App: http://localhost:3000
# API: http://localhost:8000
```

---

## ⚙️ Environment Variables

Create `backend/.env` from `backend/.env.example`:

```env
# MongoDB (required)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=resume_builder

# JWT (required — change in production!)
JWT_SECRET_KEY=your-super-secret-key

# AI — Agent 1: Groq (optional — app works without it)
GROQ_API_KEY=gsk_...
AGENT1_MODEL=llama-3.3-70b-versatile

# Agent 2 uses the same Groq API key and model as Agent 1.

# PDF Backend
LATEX_BACKEND=latexonline   # or: local (requires pdflatex)
```

> **No API keys?** The app runs in **fallback mode** — deterministic heuristics handle all AI tasks.

---

## 📋 API Reference

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register new user |
| `POST` | `/api/v1/auth/login` | Login → JWT tokens |
| `POST` | `/api/v1/auth/refresh` | Refresh access token |
| `GET`  | `/api/v1/auth/me` | Current user info |

### Profiles
| Method | Endpoint | Description |
|---|---|---|
| `GET`  | `/api/v1/profiles/me` | Get/auto-create profile |
| `PUT`  | `/api/v1/profiles/me` | Update profile fields |

### Resumes
| Method | Endpoint | Description |
|---|---|---|
| `GET`  | `/api/v1/resumes` | List resumes (paginated) |
| `POST` | `/api/v1/resumes` | Create + run AI pipeline |
| `GET`  | `/api/v1/resumes/{id}` | Get resume detail |
| `PUT`  | `/api/v1/resumes/{id}` | Update resume |
| `DELETE` | `/api/v1/resumes/{id}` | Delete resume |
| `POST` | `/api/v1/resumes/{id}/duplicate` | Clone resume |
| `POST` | `/api/v1/resumes/{id}/export/pdf` | Export as PDF |

### AI Agents
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/agents/rewrite-bullet` | XYZ bullet rewriter |
| `POST` | `/api/v1/agents/ats-audit` | ATS compliance score |
| `POST` | `/api/v1/agents/tailor-to-jd` | JD gap analysis |
| `POST` | `/api/v1/agents/generate-summary` | Executive summary |
| `GET`  | `/api/v1/agents/models` | Model status |

---

## 🎨 Resume Templates

| Template | Style | Best For |
|---|---|---|
| `executive` | ATS Monochrome (Jake's Resume) | Corporate & engineering |
| `modern` | Tech Minimal | Startups & FAANG |
| `classic` | Harvard Serif Academic | Research & finance |
| `compact` | Two-Column Dense | Senior engineers |

---

## 🧪 Testing

**Backend:**
```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

**Frontend:**
```bash
cd frontend
npm test
```

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI 0.115 · Python 3.11 · Pydantic v2 |
| Database | MongoDB 7 · Motor 3 (async) |
| Auth | JWT (HS256) · bcrypt |
| AI LLMs | Groq (llama-3.3-70b) · Mistral (final polish) |
| PDF | LaTeX → latexonline.cc or local pdflatex |
| Frontend | React 18 · Vite 5 · TypeScript 5 · Tailwind CSS 3 |
| State | Zustand 5 |
| Tests | pytest-asyncio · Vitest |
| CI/CD | GitHub Actions → GHCR Docker images |
| Containers | Docker · Docker Compose |

---

## 📄 License

MIT © 2024 Rahul Kate
