"""
admin/routes/signals.py — Signal snapshot and signal management endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from shared.db import get_pool
from admin.dependencies import verify_admin_secret

router = APIRouter(prefix="/signals", tags=["Signals"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class SnapshotCreate(BaseModel):
    pips_closed:   float = 0.0
    pips_floating: float = 0.0
    pips_week:     float = 0.0
    pips_month:    float = 0.0
    closed_count:  int   = 0
    open_count:    int   = 0


class SignalUpdate(BaseModel):
    status:      Optional[str]   = None
    pips_result: Optional[float] = None


# ── Signal Snapshot Endpoints ─────────────────────────────────────────────────

@router.get("/snapshots", dependencies=[Depends(verify_admin_secret)])
async def list_snapshots():
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM signal_snapshots ORDER BY snapshot_date DESC LIMIT 90"
    )
    return [dict(r) for r in rows]


@router.post("/snapshots", dependencies=[Depends(verify_admin_secret)])
async def create_snapshot(body: SnapshotCreate):
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO signal_snapshots
            (pips_closed, pips_floating, pips_week, pips_month, closed_count, open_count)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (snapshot_date)
        DO UPDATE SET
            pips_closed   = EXCLUDED.pips_closed,
            pips_floating = EXCLUDED.pips_floating,
            pips_week     = EXCLUDED.pips_week,
            pips_month    = EXCLUDED.pips_month,
            closed_count  = EXCLUDED.closed_count,
            open_count    = EXCLUDED.open_count,
            created_at    = NOW()
        RETURNING *
        """,
        body.pips_closed, body.pips_floating,
        body.pips_week, body.pips_month,
        body.closed_count, body.open_count,
    )
    return dict(row)


# ── Signal Endpoints ──────────────────────────────────────────────────────────

@router.get("", dependencies=[Depends(verify_admin_secret)])
async def list_signals():
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM signals ORDER BY created_at DESC LIMIT 100"
    )
    return [dict(r) for r in rows]


@router.patch("/{signal_id}", dependencies=[Depends(verify_admin_secret)])
async def update_signal(signal_id: int, body: SignalUpdate):
    pool = await get_pool()

    existing = await pool.fetchrow("SELECT id FROM signals WHERE id = $1", signal_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Signal not found")

    valid_statuses = {"open", "tp1", "tp2", "tp3", "sl", "be", "partial", "closed"}
    if body.status and body.status not in valid_statuses:
        raise HTTPException(status_code=422, detail=f"Invalid status. Must be one of: {valid_statuses}")

    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=422, detail="No fields provided to update")

    fields = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates))
    values = list(updates.values())

    # Auto-set closed_at when closing
    if body.status in ("tp1", "tp2", "tp3", "sl", "be", "partial", "closed"):
        fields += f", closed_at = NOW()"

    row = await pool.fetchrow(
        f"UPDATE signals SET {fields} WHERE id = $1 RETURNING *",
        signal_id, *values,
    )
    return dict(row)
