"""
shared/db.py — Async PostgreSQL connection pool (asyncpg)
Shared by all bots and the admin API.
"""
import os
import asyncpg
from shared.logger import get_logger

logger = get_logger("db")

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Return the shared connection pool, creating it on first call."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ.get("POSTGRES_PORT", 5432)),
            database=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            min_size=2,
            max_size=10,
            command_timeout=30,
        )
        logger.info("PostgreSQL connection pool created")
    return _pool


async def close_pool() -> None:
    """Close the connection pool on shutdown."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("PostgreSQL connection pool closed")
