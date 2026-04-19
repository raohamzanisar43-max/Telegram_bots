"""
signals_bot/handlers.py — Command handlers for P1 Signals Bot
"""
from datetime import date
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from shared.db import get_pool
from shared.i18n import t
from shared.logger import get_logger

logger = get_logger("signals-bot")

BOT_NAME = "P1 Signals Bot"

COMMANDS_EN = (
    "/subscribe — Subscribe to daily reports\n"
    "/unsubscribe — Stop reports\n"
    "/daily — Today's report\n"
    "/performance — Latest snapshot\n"
    "/setlot 0.1 — Set your lot size\n"
    "/setlang en|de — Change language\n"
    "/help — This message"
)

COMMANDS_DE = (
    "/subscribe — Tägliche Berichte aktivieren\n"
    "/unsubscribe — Berichte stoppen\n"
    "/daily — Heutiger Bericht\n"
    "/performance — Neuester Snapshot\n"
    "/setlot 0.1 — Lotgröße setzen\n"
    "/setlang en|de — Sprache ändern\n"
    "/help — Diese Nachricht"
)


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
    lang = user["language"]
    await update.message.reply_text(
        t("welcome", lang, bot_name=BOT_NAME),
        parse_mode=ParseMode.MARKDOWN,
    )


async def subscribe(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    existing = await pool.fetchrow(
        "SELECT active FROM subscriptions WHERE user_id = $1 AND bot = 'signals'",
        user["id"],
    )
    lang = user["language"]
    if existing and existing["active"]:
        await update.message.reply_text(t("already_subscribed", lang))
        return
    await pool.execute(
        "INSERT INTO subscriptions (user_id, bot, active) VALUES ($1, 'signals', TRUE) "
        "ON CONFLICT (user_id, bot) DO UPDATE SET active = TRUE",
        user["id"],
    )
    await update.message.reply_text(t("subscribed", lang))


async def unsubscribe(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    lang = user["language"]
    result = await pool.execute(
        "UPDATE subscriptions SET active = FALSE WHERE user_id = $1 AND bot = 'signals' AND active = TRUE",
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
    await pool.execute(
        "UPDATE users SET language = $1 WHERE id = $2", lang, user["id"]
    )
    await update.message.reply_text(t("language_set", lang))


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    lang = user["language"]
    commands = COMMANDS_DE if lang == "de" else COMMANDS_EN
    await update.message.reply_text(t("help", lang, commands=commands))


async def daily(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    lang = user["language"]

    snap = await pool.fetchrow(
        "SELECT * FROM signal_snapshots ORDER BY snapshot_date DESC LIMIT 1"
    )
    if not snap:
        await update.message.reply_text(t("no_data", lang))
        return

    settings = await pool.fetchrow(
        "SELECT lot_size FROM user_signals_settings WHERE user_id = $1", user["id"]
    )
    lot = float(settings["lot_size"]) if settings else 0.10
    pnl = float(snap["pips_closed"]) * lot * 10  # rough estimate: $10 per pip per lot

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

    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def performance(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Alias for /daily."""
    await daily(update, ctx)


async def setlot(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    lang = user["language"]
    try:
        lot = float(ctx.args[0])
        assert 0.01 <= lot <= 100
    except (IndexError, ValueError, AssertionError):
        await update.message.reply_text(t("lot_invalid", lang))
        return
    await pool.execute(
        "INSERT INTO user_signals_settings (user_id, lot_size) VALUES ($1, $2) "
        "ON CONFLICT (user_id) DO UPDATE SET lot_size = $2",
        user["id"], lot,
    )
    await update.message.reply_text(t("lot_set", lang, lot_size=lot))
