"""
funded_bot/scheduler.py — Cron job for P3 Funded Bot
  - 20:30 UTC: broadcast daily challenge status to all active funded accounts
"""
import datetime
from telegram.ext import Application
from telegram.constants import ParseMode

from shared.db import get_pool
from shared.logger import get_logger
from funded_bot.rules import build_status_message

logger = get_logger("funded-bot")


async def broadcast_daily(context) -> None:
    """Send daily funded account status to all active accounts at 20:30."""
    pool = await get_pool()

    rows = await pool.fetch(
        """
        SELECT u.telegram_id, u.language, fa.*
        FROM funded_accounts fa
        JOIN users u ON u.id = fa.user_id
        JOIN subscriptions sub ON sub.user_id = fa.user_id AND sub.bot = 'funded'
        WHERE fa.active = TRUE AND sub.active = TRUE
        """
    )

    sent = 0
    for row in rows:
        lang    = row["language"]
        account = dict(row)
        msg     = build_status_message(account, lang)

        try:
            await context.bot.send_message(
                chat_id=row["telegram_id"],
                text=msg,
                parse_mode=ParseMode.MARKDOWN,
            )
            sent += 1
        except Exception as e:
            logger.warning(f"Failed to send to {row['telegram_id']}: {e}")

    logger.info(f"broadcast_daily: sent to {sent}/{len(rows)} funded accounts")


def schedule_jobs(app: Application) -> None:
    jq = app.job_queue
    jq.run_daily(
        broadcast_daily,
        time=datetime.time(hour=20, minute=30, tzinfo=datetime.timezone.utc),
        name="funded_daily_broadcast",
    )
    logger.info("Funded Bot scheduler registered (20:30 UTC daily)")
