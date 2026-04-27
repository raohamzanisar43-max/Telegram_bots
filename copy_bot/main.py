"""
copy_bot/main.py — P2 Copy Bot entry point
"""
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

from shared.db import get_pool, close_pool
from shared.logger import get_logger
from copy_bot.handlers import (
    start, subscribe, unsubscribe, setlang, help_cmd,
    daily, projection, setdeposit, setrisk,
)
from copy_bot.scheduler import schedule_jobs

load_dotenv()
logger = get_logger("copy-bot")


async def post_init(app: Application) -> None:
    await get_pool()
    logger.info("Copy Bot started")


async def post_shutdown(app: Application) -> None:
    await close_pool()
    logger.info("Copy Bot stopped")


async def main() -> None:
    token = os.environ["COPY_BOT_TOKEN"]

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
    app.add_handler(CommandHandler("daily",       daily))
    app.add_handler(CommandHandler("projection",  projection))
    app.add_handler(CommandHandler("setdeposit",  setdeposit))
    app.add_handler(CommandHandler("setrisk",     setrisk))

    schedule_jobs(app)

    logger.info("Copy Bot polling...")
    await app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
