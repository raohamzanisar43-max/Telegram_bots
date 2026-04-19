"""
admin/routes/funded.py — Funded account CRUD endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from shared.db import get_pool
from admin.dependencies import verify_admin_secret

router = APIRouter(prefix="/funded", tags=["Funded Accounts"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class FundedCreate(BaseModel):
    telegram_id:      int
    account_size:     float = Field(..., gt=0)
    profit_target:    float = Field(..., gt=0, le=100)
    max_daily_loss:   float = Field(..., gt=0, le=100)
    max_overall_loss: float = Field(..., gt=0, le=100)
    phase:            str   = Field(default="challenge")


class FundedUpdate(BaseModel):
    current_gain:      Optional[float] = None
    used_daily_loss:   Optional[float] = None
    used_overall_loss: Optional[float] = None
    phase:             Optional[str]   = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", dependencies=[Depends(verify_admin_secret)])
async def list_funded():
    pool = await get_pool()
    rows = await pool.fetch(
        """
        SELECT fa.*, u.telegram_id, u.username
        FROM funded_accounts fa
        JOIN users u ON u.id = fa.user_id
        ORDER BY fa.created_at DESC
        """
    )
    return [dict(r) for r in rows]


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_admin_secret)])
async def create_funded(body: FundedCreate):
    pool = await get_pool()

    # User must have /started the bot already
    user = await pool.fetchrow(
        "SELECT id FROM users WHERE telegram_id = $1", body.telegram_id
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. The user must /start the bot first.",
        )

    row = await pool.fetchrow(
        """
        INSERT INTO funded_accounts
            (user_id, account_size, profit_target, max_daily_loss, max_overall_loss, phase)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING *
        """,
        user["id"],
        body.account_size,
        body.profit_target,
        body.max_daily_loss,
        body.max_overall_loss,
        body.phase,
    )
    return dict(row)


@router.patch("/{account_id}", dependencies=[Depends(verify_admin_secret)])
async def update_funded(account_id: int, body: FundedUpdate):
    pool = await get_pool()

    existing = await pool.fetchrow(
        "SELECT id FROM funded_accounts WHERE id = $1 AND active = TRUE", account_id
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Funded account not found or inactive")

    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=422, detail="No fields provided to update")

    # Build dynamic SET clause
    fields = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates))
    values = list(updates.values())

    row = await pool.fetchrow(
        f"UPDATE funded_accounts SET {fields}, updated_at = NOW() "
        f"WHERE id = $1 RETURNING *",
        account_id, *values,
    )
    return dict(row)


@router.delete("/{account_id}", dependencies=[Depends(verify_admin_secret)])
async def deactivate_funded(account_id: int):
    pool = await get_pool()
    result = await pool.execute(
        "UPDATE funded_accounts SET active = FALSE, updated_at = NOW() WHERE id = $1 AND active = TRUE",
        account_id,
    )
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Funded account not found or already inactive")
    return {"message": f"Account {account_id} deactivated"}
