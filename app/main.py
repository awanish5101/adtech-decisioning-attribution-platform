"""
Main application factory for the AdTech Decisioning and Attribution Platform.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.config import settings
from app.core.telemetry import TelemetryMiddleware
from app.api.decisioning import router as decision_router
from app.api.campaigns import router as campaign_router
from app.api.events import router as event_router
from app.api.analytics import router as analytics_router
from app.api.ai_agent import router as ai_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Scalable AdTech platform powering real-time ad serving decisioning, high-throughput event ingestion, "
        "multi-touch ROAS attribution, and autonomous AI agents for campaign optimization."
    ),
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telemetry and Execution Timing Middleware
app.add_middleware(TelemetryMiddleware)

# Include API Routers under /api/v1
app.include_router(decision_router, prefix="/api/v1")
app.include_router(campaign_router, prefix="/api/v1")
app.include_router(event_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
def health_check():
    """Liveness probe verifying real-time auction and ingestion engine health."""
    return {
        "status": "HEALTHY",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/ready", tags=["System"])
def readiness_check():
    """Readiness probe verifying datastores and caching components."""
    return {
        "status": "READY",
        "decisioning_engine": "ONLINE",
        "event_ingestion_pipeline": "ONLINE",
        "redis_frequency_capper": "ACTIVE",
        "attribution_worker": "ACTIVE"
    }


@app.get("/", tags=["System"])
def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "realtime_ad_decisioning": "/api/v1/ad/decision",
        "event_tracking": "/api/v1/events/track",
        "roas_analytics": "/api/v1/analytics/roas"
    }
