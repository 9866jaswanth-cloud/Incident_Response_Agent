"""Incident Response Agent - Main FastAPI Entrypoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.memory import router as memory_router
from app.api.agent import router as agent_router
from app.api.incidents import router as incidents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print(f"[*] Starting {settings.PROJECT_NAME}")
    print(f"[*] Hindsight Bank: {settings.HINDSIGHT_BANK_ID} at {settings.HINDSIGHT_BASE_URL}")
    yield
    # Shutdown actions
    print(f"[*] Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.TAGLINE,
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include Routers
app.include_router(memory_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(incidents_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "environment": settings.ENVIRONMENT,
        "hindsight_target": settings.HINDSIGHT_BASE_URL,
        "hindsight_bank": settings.HINDSIGHT_BANK_ID,
    }


# Mount compiled React frontend if built
from pathlib import Path
from fastapi.staticfiles import StaticFiles

dist_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if dist_path.exists() and (dist_path / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="static_frontend")
