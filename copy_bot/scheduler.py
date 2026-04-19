"""
copy_bot/scheduler.py — Cron jobs for P2 Copy Bot
  - Every hour: fetch MT4 master snapshot
  - 20:00 UTC: broadcast personalised report to all subscribers
"""
import datetime
from telegram.ext import Application
from telegram.constants import ParseMode

from shared.db import get_pool
from shared.i18n import t
from shared.logger import get_logger
from copy_bot.metaapi_client import fetch_mt4_snapshot
from copy_bot.compounding import user_balance_today

logger = get_logger("copy-bot")


async def fetch_and_store_snapshot(context) -> None:
    """Fetch MT4 data every hour and store in master_snapshots."""
    pool = await get_pool()
    data = await fetch_mt4_snapshot()

    if data is None:
        logger.warning("fetch_and_store_snapshot: no MT4 data — snapshot skipped")
        return

    # Compute daily/weekly/monthly returns vs previous snapshots
    prev_day = await pool.fetchrow(
        "SELECT equity FROM master_snapshots "
        "WHERE snapshot_ts < NOW() - INTERVAL '23 hours' "
        "ORDER BY snapshot_ts DESC LIMIT 1"
    )
    prev_week = await pool.fetchrow(
        "SELECT equity FROM master_snapshots "
        "WHERE snapshot_ts < NOW() - INTERVAL '6 days 23 hours' "
        "ORDER BY snapshot_ts DESC LIMIT 1"
    )
    prev_month = await pool.fetchrow(
        "SELECT equity FROM master_snapshots "
        "WHERE snapshot_ts < NOW() - INTERVAL '29 days 23 hours' "
        "ORDER BY snapshot_ts DESC LIMIT 1"
    )

    equity = data["equity"]

    def pct_change(prev_row) -> float | None:
        if not prev_row:
            return None
        prev_eq = float(prev_row["equity"])
        if prev_eq == 0:
            return None
        return (equity - prev_eq) / prev_eq * 100

    # Simple drawdown: max drop from peak this month
    peak = await pool.fetchrow(
        "SELECT MAX(equity) AS peak FROM master_snapshots "
        "WHERE snapshot_ts > NOW() - INTERVAL '30 days'"
    )
    drawdown = 0.0
    if peak and peak["peak"]:
        peak_val = float(peak["peak"])
        drawdown = max(0.0, (peak_val - equity) / peak_val * 100) if peak_val else 0.0

    await pool.execute(
        """
        INSERT INTO master_snapshots
            (equity, balance, floating_pnl_pct,
             return_day_pct, return_week_pct, return_month_pct, drawdown_month, source)
        VALUES ($1, $2, $3, $4, $5, $6, $7, 'api')
        """,
        equity,
        data["balance"],
        data["floating_pnl_pct"],
        pct_change(prev_day),
        pct_change(prev_week),
        pct_change(prev_month),
        drawdown,
    )
    logger.info(f"Stored MT4 snapshot — equity={equity}")


async def broadcast_daily(context) -> None:
    """Broadcast personalised daily report to all copy-bot subscribers at 20:00."""
    pool = await get_pool()

    snap = await pool.fetchrow(
        "SELECT * FROM master_snapshots ORDER BY snapshot_ts DESC LIMIT 1"
    )
    if not snap:
        logger.warning("broadcast_daily: no master snapshot available")
        return

    subscribers = await pool.fetch(
        """
        SELECT u.telegram_id, u.language,
               COALESCE(cs.deposit, 1000)         AS deposit,
               COALESCE(cs.risk_multiplier, 1.0)  AS risk_multiplier,
               COALESCE(cs.reinvest, TRUE)         AS reinvest
        FROM subscriptions sub
        JOIN users u ON u.id = sub.user_id
        LEFT JOIN user_copy_settings cs ON cs.user_id = u.id
        WHERE sub.bot = 'copy' AND sub.active = TRUE
        """
    )

    sent = 0
    for row in subscribers:
        lang     = row["language"]
        deposit  = float(row["deposit"])
        risk     = float(row["risk_multiplier"])
        reinvest = row["reinvest"]

        balance = user_balance_today(
            deposit=deposit,
            daily_pct=float(snap["return_day_pct"] or 0),
            risk_multiplier=risk,
            reinvest=reinvest,
        )

        msg = t(
            "copy_daily", lang,
            date=snap["snapshot_ts"].strftime("%d %b %Y"),
            balance=balance,
            return_day_pct=float(snap["return_day_pct"] or 0) * risk,
            return_week_pct=float(snap["return_week_pct"] or 0) * risk,
            return_month_pct=float(snap["return_month_pct"] or 0) * risk,
            drawdown_month=float(snap["drawdown_month"] or 0),
            floating_pnl_pct=float(snap["floating_pnl_pct"] or 0),
        ) + t("compliance_footer", lang)

        try:
            await context.bot.send_message(
                chat_id=row["telegram_id"],
                text=msg,
                parse_mode=ParseMode.MARKDOWN,
            )
            sent += 1
        except Exception as e:
            logger.warning(f"Failed to send to {row['telegram_id']}: {e}")

    logger.info(f"broadcast_daily: sent to {sent}/{len(subscribers)} subscribers")


def schedule_jobs(app: Application) -> None:
    jq = app.job_queue
    # Every hour — fetch MT4 data
    jq.run_repeating(
        fetch_and_store_snapshot,
        interval=3600,
        first=10,
        name="copy_mt4_fetch",
    )
    # Every day at 20:00 UTC — send reports
    jq.run_daily(
        broadcast_daily,
        time=datetime.time(hour=20, minute=0, tzinfo=datetime.timezone.utc),
        name="copy_daily_broadcast",
    )
    logger.info("Copy Bot scheduler registered (hourly fetch + 20:00 UTC broadcast)")
