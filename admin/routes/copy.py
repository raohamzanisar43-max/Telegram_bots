"""
admin/routes/copy.py — Master snapshot manual override endpoints (P2 fallback)
"""
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from shared.db import get_pool
from admin.dependencies import verify_admin_secret

router = APIRouter(prefix="/copy", tags=["Copy Bot"])


class SnapshotOverride(BaseModel):
    return_day_pct:   Optional[float] = None
    return_week_pct:  Optional[float] = None
    return_month_pct: Optional[float] = None
    drawdown_month:   Optional[float] = None
    floating_pnl_pct: Optional[float] = None
    equity:           Optional[float] = None
    balance:          Optional[float] = None


@router.get("/snapshots", dependencies=[Depends(verify_admin_secret)])
async def list_snapshots():
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM master_snapshots ORDER BY snapshot_ts DESC LIMIT 90"
    )
    return [dict(r) for r in rows]


@router.post("/snapshots", dependencies=[Depends(verify_admin_secret)])
async def manual_snapshot(body: SnapshotOverride):
    """
    Manual override for master snapshot — used when MT4 connection fails.
    Source is recorded as 'manual'.
    """
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO master_snapshots
            (return_day_pct, return_week_pct, return_month_pct,
             drawdown_month, floating_pnl_pct, equity, balance, source)
        VALUES ($1, $2, $3, $4, $5, $6, $7, 'manual')
        RETURNING *
        """,
        body.return_day_pct,
        body.return_week_pct,
        body.return_month_pct,
        body.drawdown_month,
        body.floating_pnl_pct,
        body.equity,
        body.balance,
    )
    return dict(row)
