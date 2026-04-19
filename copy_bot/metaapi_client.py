"""
copy_bot/metaapi_client.py — MT4 read-only connection via MetaAPI.cloud SDK
Falls back to mock data and logs a warning if connection fails.
Do NOT patch the fallback — fix the credentials instead.
"""
import os
from shared.logger import get_logger

logger = get_logger("copy-bot")


async def fetch_mt4_snapshot() -> dict | None:
    """
    Fetch current equity, balance, and floating P&L from MT4 master account.
    Returns a dict or None on failure (caller stores fallback warning).
    """
    token      = os.environ.get("META_API_TOKEN", "")
    account_id = os.environ.get("MT4_ACCOUNT_ID", "")

    if not token or not account_id:
        logger.warning("MetaAPI credentials missing — skipping MT4 fetch")
        return None

    try:
        from metaapi_cloud_sdk import MetaApi  # type: ignore

        api     = MetaApi(token)
        account = await api.metatrader_account_api.get_account(account_id)

        # Ensure account is connected
        if account.state not in ("DEPLOYED", "DEPLOYING"):
            await account.deploy()
        await account.wait_connected()

        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_synchronized()

        info = await connection.get_account_information()

        equity  = float(info.get("equity", 0))
        balance = float(info.get("balance", 0))
        profit  = float(info.get("profit", 0))

        floating_pnl_pct = (profit / balance * 100) if balance else 0.0

        await connection.close()

        logger.info(f"MT4 snapshot fetched — equity={equity} balance={balance}")
        return {
            "equity":           equity,
            "balance":          balance,
            "floating_pnl_pct": floating_pnl_pct,
        }

    except Exception as e:
        logger.warning(f"MetaAPI fetch failed: {e} — falling back to mock data")
        return None
