"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.companies import router as companies_router
from app.api.contacts import router as contacts_router
from app.api.mandates import router as mandates_router
from app.api.schedule import router as schedule_router
from app.api.users import router as users_router
from app.core.config import settings

app = FastAPI(
    title="Project Upstream API",
    description="M&A deal-sourcing CRM backend.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(mandates_router)
app.include_router(companies_router)
app.include_router(contacts_router)
app.include_router(schedule_router)
app.include_router(analytics_router)
app.include_router(users_router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
