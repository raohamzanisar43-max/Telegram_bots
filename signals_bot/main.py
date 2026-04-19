"""
signals_bot/main.py — P1 Signals Bot entry point
"""
import asyncio
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from shared.db import get_pool, close_pool
from shared.logger import get_logger
from signals_bot.handlers import (
    start, subscribe, unsubscribe, setlang, help_cmd,
    daily, performance, setlot,
)
from signals_bot.channel_listener import channel_post_handler
from signals_bot.scheduler import schedule_jobs

load_dotenv()
logger = get_logger("signals-bot")


async def post_init(app: Application) -> None:
    await get_pool()
    logger.info("Signals Bot started")


async def post_shutdown(app: Application) -> None:
    await close_pool()
    logger.info("Signals Bot stopped")


def main() -> None:
    token = os.environ["SIGNALS_BOT_TOKEN"]

    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Commands
    app.add_handler(CommandHandler("start",       start))
    app.add_handler(CommandHandler("subscribe",   subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CommandHandler("setlang",     setlang))
    app.add_handler(CommandHandler("help",        help_cmd))
    app.add_handler(CommandHandler("daily",       daily))
    app.add_handler(CommandHandler("performance", performance))
    app.add_handler(CommandHandler("setlot",      setlot))

    # Channel post listener (VIP channel)
    channel_id = int(os.environ["SIGNALS_VIP_CHANNEL_ID"])
    app.add_handler(
        MessageHandler(
            filters.Chat(channel_id) & filters.UpdateType.CHANNEL_POST,
            channel_post_handler,
        )
    )

    # Scheduled jobs
    schedule_jobs(app)

    logger.info("Signals Bot polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
