"""
admin/main.py — FastAPI Admin API entry point
Port 4000 — localhost only. Use nginx with auth if external access is needed.
"""
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI

from shared.db import get_pool, close_pool
from shared.logger import get_logger
from admin.routes.funded import router as funded_router
from admin.routes.signals import router as signals_router
from admin.routes.copy import router as copy_router
from admin.routes.health import router as health_router

load_dotenv()
logger = get_logger("admin-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    logger.info("Admin API started on port 4000")
    yield
    await close_pool()
    logger.info("Admin API stopped")


app = FastAPI(
    title="Profitability Intelligence — Admin API",
    version="1.0.0",
    description="Internal admin API for PI bots. Localhost only.",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(funded_router)
app.include_router(signals_router)
app.include_router(copy_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=4000, log_level="info")
