"""
admin/routes/health.py — Health check endpoint (no auth required)
"""
from fastapi import APIRouter
from shared.db import get_pool

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    """
    Returns service status and DB connectivity.
    Used by: docker compose healthcheck, monitoring, curl http://localhost:4000/health
    """
    try:
        pool = await get_pool()
        await pool.fetchval("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "status":  "ok" if db_status == "ok" else "degraded",
        "service": "profitability-intelligence-admin",
        "db":      db_status,
    }
