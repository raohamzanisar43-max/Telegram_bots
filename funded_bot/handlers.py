"""
funded_bot/handlers.py — Command handlers for P3 Funded Bot
"""
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from shared.db import get_pool
from shared.i18n import t
from shared.logger import get_logger
from funded_bot.rules import build_status_message

logger = get_logger("funded-bot")

BOT_NAME = "P3 Funded Bot"


async def _get_or_create_user(pool, tg_user) -> dict:
    row = await pool.fetchrow(
        "SELECT id, language FROM users WHERE telegram_id = $1", tg_user.id
    )
    if row is None:
        await pool.execute(
            "INSERT INTO users (telegram_id, username, first_name) VALUES ($1, $2, $3) "
            "ON CONFLICT DO NOTHING",
            tg_user.id, tg_user.username, tg_user.first_name,
        )
        row = await pool.fetchrow(
            "SELECT id, language FROM users WHERE telegram_id = $1", tg_user.id
        )
    return dict(row)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    await update.message.reply_text(
        t("welcome", user["language"], bot_name=BOT_NAME),
        parse_mode=ParseMode.MARKDOWN,
    )


async def subscribe(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    lang = user["language"]
    existing = await pool.fetchrow(
        "SELECT active FROM subscriptions WHERE user_id = $1 AND bot = 'funded'",
        user["id"],
    )
    if existing and existing["active"]:
        await update.message.reply_text(t("already_subscribed", lang))
        return
    await pool.execute(
        "INSERT INTO subscriptions (user_id, bot, active) VALUES ($1, 'funded', TRUE) "
        "ON CONFLICT (user_id, bot) DO UPDATE SET active = TRUE",
        user["id"],
    )
    await update.message.reply_text(t("subscribed", lang))


async def unsubscribe(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    lang = user["language"]
    result = await pool.execute(
        "UPDATE subscriptions SET active = FALSE "
        "WHERE user_id = $1 AND bot = 'funded' AND active = TRUE",
        user["id"],
    )
    if result == "UPDATE 0":
        await update.message.reply_text(t("not_subscribed", lang))
    else:
        await update.message.reply_text(t("unsubscribed", lang))


async def setlang(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    args = ctx.args
    if not args or args[0] not in ("en", "de"):
        await update.message.reply_text("Usage: /setlang en|de")
        return
    lang = args[0]
    await pool.execute("UPDATE users SET language = $1 WHERE id = $2", lang, user["id"])
    await update.message.reply_text(t("language_set", lang))


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    lang = user["language"]
    commands = (
        "/subscribe — Subscribe to daily updates\n"
        "/unsubscribe — Stop updates\n"
        "/status — Current account status\n"
        "/performance — Same as /status\n"
        "/setlang en|de — Change language\n"
        "/help — This message"
    )
    await update.message.reply_text(t("help", lang, commands=commands))


async def status(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    lang = user["language"]

    account = await pool.fetchrow(
        "SELECT * FROM funded_accounts WHERE user_id = $1 AND active = TRUE LIMIT 1",
        user["id"],
    )

    if not account:
        await update.message.reply_text(t("funded_no_account", lang))
        return

    msg = build_status_message(dict(account), lang)
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


# /performance is an alias for /status
performance = status
