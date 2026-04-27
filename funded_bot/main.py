"""
funded_bot/main.py — P3 Funded Bot entry point
"""
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

from shared.db import get_pool, close_pool
from shared.logger import get_logger
from funded_bot.handlers import (
    start, subscribe, unsubscribe, setlang, help_cmd,
    status, performance,
)
from funded_bot.scheduler import schedule_jobs

load_dotenv()
logger = get_logger("funded-bot")


async def post_init(app: Application) -> None:
    await get_pool()
    logger.info("Funded Bot started")


async def post_shutdown(app: Application) -> None:
    await close_pool()
    logger.info("Funded Bot stopped")


async def main() -> None:
    token = os.environ["FUNDED_BOT_TOKEN"]

    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start",       start))
    app.add_handler(CommandHandler("subscribe",   subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CommandHandler("setlang",     setlang))
    app.add_handler(CommandHandler("help",        help_cmd))
    app.add_handler(CommandHandler("status",      status))
    app.add_handler(CommandHandler("performance", performance))

    schedule_jobs(app)

    logger.info("Funded Bot polling...")
    await app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
