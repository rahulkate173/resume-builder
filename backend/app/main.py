"""
backend/app/main.py
FastAPI application factory with lifespan, CORS, middleware, and routers.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import ping, shutdown, startup
from app.routers import auth, profiles, resumes, agents
from app.routers import jd_resume

settings = get_settings()


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database connection lifecycle."""
    await startup()
    yield
    await shutdown()


# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## AI Resume Builder API

Production-grade resume builder with a **LangGraph multi-agent AI** pipeline:
- **Gemini via LangChain**: LaTeX resume generation, JD tailoring, and quality verification
- **LangGraph**: Orchestrates agent stages, review loops, and PDF compilation

### Features
- JWT authentication with refresh tokens
- Full resume CRUD + versioning
- ATS auditing & bullet rewriting
- JD gap analysis & match scoring
- PDF export with LaTeX compilation
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── Middleware ─────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ── Global exception handler ──────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error.", "type": type(exc).__name__},
    )


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/api/v1/health", tags=["health"])
async def health():
    db_ok = await ping()
    return {
        "status": "healthy" if db_ok else "degraded",
        "version": settings.app_version,
        "database": "connected" if db_ok else "disconnected",
        "ai_available": settings.ai_available,
        "fallback_mode": not settings.ai_available,
    }


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(resumes.router)
app.include_router(agents.router)
app.include_router(jd_resume.router)


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
