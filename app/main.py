"""FastAPI application entry point."""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR, get_settings
from app.api.auth import router as auth_router
from app.api.events import router as events_router
from app.api.registrations import router as registrations_router
from app.api.fraud import router as fraud_router
from app.api.payments import router as payments_router
from app.api.tickets import router as tickets_router
from app.api.attendance import router as attendance_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Event Registration System",
    version="0.1.0",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(events_router, prefix="/api/events", tags=["events"])
app.include_router(registrations_router, prefix="/api/registrations", tags=["registrations"])
app.include_router(fraud_router, prefix="/api/fraud", tags=["fraud"])
app.include_router(payments_router, prefix="/api/payments", tags=["payments"])
app.include_router(tickets_router, prefix="/api/tickets", tags=["tickets"])
app.include_router(attendance_router, prefix="/api/attendance", tags=["attendance"])

# Static files
static_dir = settings.static_dir
static_dir.mkdir(parents=True, exist_ok=True)
(static_dir / "css").mkdir(parents=True, exist_ok=True)
(static_dir / "js").mkdir(parents=True, exist_ok=True)
(static_dir / "images").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates = Jinja2Templates(directory=str(settings.templates_dir))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "success": True,
        "status": "healthy",
        "app": settings.app_name,
        "version": "0.1.0",
        "demo_mode": settings.demo_mode,
    }


@app.get("/api/stats")
async def landing_stats():
    """Landing page statistics — will connect to DB in later phases."""
    return {
        "success": True,
        "data": {
            "total_registrations": 10247,
            "security_rate": 99.9,
            "total_events": 52,
            "attendance_rate": 95.0,
        },
    }


# ── Frontend pages ──────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Animated landing page."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "app_name": settings.app_name,
            "demo_mode": settings.demo_mode,
        },
    )


@app.get("/events", response_class=HTMLResponse)
async def events_page(request: Request):
    """Events listing — placeholder for Phase 4."""
    return templates.TemplateResponse(
        request,
        "events.html",
        {"app_name": settings.app_name},
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page — placeholder for Phase 3."""
    return templates.TemplateResponse(
        request,
        "login.html",
        {"app_name": settings.app_name},
    )


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup page — placeholder for Phase 3."""
    return templates.TemplateResponse(
        request,
        "signup.html",
        {"app_name": settings.app_name},
    )


@app.on_event("startup")
async def on_startup():
    logger.info("Starting %s", settings.app_name)
    logger.info("Debug mode: %s", settings.debug)
    logger.info("Demo mode: %s", settings.demo_mode)
