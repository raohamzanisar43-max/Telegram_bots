"""
admin/dependencies.py — FastAPI dependency: validates X-Admin-Secret header
"""
import os
from fastapi import Header, HTTPException, status


async def verify_admin_secret(x_admin_secret: str = Header(...)) -> None:
    """
    Validates the X-Admin-Secret header against ADMIN_SECRET env var.
    Raises 403 if missing or incorrect.
    """
    expected = os.environ.get("ADMIN_SECRET", "")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_SECRET not configured on server",
        )
    if x_admin_secret != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin secret",
        )
