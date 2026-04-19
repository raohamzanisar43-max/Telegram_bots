"""
signals_bot/scheduler.py — Cron jobs for P1 Signals Bot
"""
import datetime
from telegram.ext import Application
from telegram.constants import ParseMode

from shared.db import get_pool
from shared.i18n import t
from shared.logger import get_logger

logger = get_logger("signals-bot")


async def broadcast_daily(context) -> None:
    """Broadcast daily report to all active subscribers at 20:00."""
    pool = await get_pool()

    snap = await pool.fetchrow(
        "SELECT * FROM signal_snapshots ORDER BY snapshot_date DESC LIMIT 1"
    )
    if not snap:
        logger.warning("broadcast_daily: no snapshot available, skipping")
        return

    subscribers = await pool.fetch(
        """
        SELECT u.telegram_id, u.language, COALESCE(s.lot_size, 0.10) AS lot_size
        FROM subscriptions sub
        JOIN users u ON u.id = sub.user_id
        LEFT JOIN user_signals_settings s ON s.user_id = u.id
        WHERE sub.bot = 'signals' AND sub.active = TRUE
        """
    )

    sent = 0
    for row in subscribers:
        lang   = row["language"]
        lot    = float(row["lot_size"])
        pnl    = float(snap["pips_closed"]) * lot * 10

        msg = t(
            "signals_daily", lang,
            date=snap["snapshot_date"].strftime("%d %b %Y"),
            closed_count=snap["closed_count"],
            pips_closed=snap["pips_closed"],
            open_count=snap["open_count"],
            pips_floating=snap["pips_floating"],
            pips_week=snap["pips_week"],
            pips_month=snap["pips_month"],
            lot_size=lot,
            pnl=pnl,
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
    # Every day at 20:00 UTC
    jq.run_daily(
        broadcast_daily,
        time=datetime.time(hour=20, minute=0, tzinfo=datetime.timezone.utc),
        name="signals_daily_broadcast",
    )
    logger.info("Signals Bot scheduler registered (20:00 UTC daily)")
