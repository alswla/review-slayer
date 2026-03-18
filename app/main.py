"""Review Slayer — FastAPI entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.webhook.handler import router as webhook_router

settings = get_settings()

# --- Logging ---
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI(
    title=settings.app_name,
    description="AI-powered multi-agent code review bot (CodeRabbit-level)",
    version="0.1.0",
)

# CORS (for future dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(webhook_router)


# --- Health Check ---
@app.get("/health", tags=["system"])
async def health_check():
    """Return application health status."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
    }
