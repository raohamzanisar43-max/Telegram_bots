"""
copy_bot/handlers.py — Command handlers for P2 Copy Bot
"""
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from shared.db import get_pool
from shared.i18n import t
from shared.logger import get_logger
from copy_bot.compounding import generate_projection, user_balance_today

logger = get_logger("copy-bot")

BOT_NAME = "P2 Copy Bot"

COMMANDS_EN = (
    "/subscribe — Subscribe to daily reports\n"
    "/unsubscribe — Stop reports\n"
    "/daily — Today's personalised report\n"
    "/projection — 12-month compounding projection\n"
    "/setdeposit 5000 — Set your deposit in USD\n"
    "/setrisk 1.0 — Set risk multiplier (0.1 – 3.0)\n"
    "/setlang en|de — Change language\n"
    "/help — This message"
)

COMMANDS_DE = (
    "/subscribe — Tägliche Berichte aktivieren\n"
    "/unsubscribe — Berichte stoppen\n"
    "/daily — Heutiger personalisierter Bericht\n"
    "/projection — 12-Monats-Compounding-Projektion\n"
    "/setdeposit 5000 — Einzahlung in USD setzen\n"
    "/setrisk 1.0 — Risikomultiplikator setzen (0.1 – 3.0)\n"
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


async def _get_copy_settings(pool, user_id: int) -> dict:
    row = await pool.fetchrow(
        "SELECT deposit, risk_multiplier, reinvest FROM user_copy_settings WHERE user_id = $1",
        user_id,
    )
    if row:
        return dict(row)
    # Insert defaults
    await pool.execute(
        "INSERT INTO user_copy_settings (user_id) VALUES ($1) ON CONFLICT DO NOTHING",
        user_id,
    )
    return {"deposit": 1000.00, "risk_multiplier": 1.00, "reinvest": True}


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
        "SELECT active FROM subscriptions WHERE user_id = $1 AND bot = 'copy'",
        user["id"],
    )
    if existing and existing["active"]:
        await update.message.reply_text(t("already_subscribed", lang))
        return
    await pool.execute(
        "INSERT INTO subscriptions (user_id, bot, active) VALUES ($1, 'copy', TRUE) "
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
        "WHERE user_id = $1 AND bot = 'copy' AND active = TRUE",
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
    commands = COMMANDS_DE if lang == "de" else COMMANDS_EN
    await update.message.reply_text(t("help", lang, commands=commands))


async def daily(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    lang = user["language"]

    snap = await pool.fetchrow(
        "SELECT * FROM master_snapshots ORDER BY snapshot_ts DESC LIMIT 1"
    )
    if not snap:
        await update.message.reply_text(t("no_data", lang))
        return

    settings = await _get_copy_settings(pool, user["id"])
    deposit  = float(settings["deposit"])
    risk     = float(settings["risk_multiplier"])
    reinvest = settings["reinvest"]

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

    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def projection(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    lang = user["language"]

    snap = await pool.fetchrow(
        "SELECT return_month_pct FROM master_snapshots ORDER BY snapshot_ts DESC LIMIT 1"
    )
    if not snap:
        await update.message.reply_text(t("no_data", lang))
        return

    settings     = await _get_copy_settings(pool, user["id"])
    deposit      = float(settings["deposit"])
    risk         = float(settings["risk_multiplier"])
    reinvest     = settings["reinvest"]
    monthly_pct  = float(snap["return_month_pct"] or 0)

    proj = generate_projection(
        deposit=deposit,
        monthly_pct=monthly_pct,
        risk_multiplier=risk,
        reinvest=reinvest,
    )

    msg = t(
        "copy_projection", lang,
        deposit=deposit,
        risk=risk,
        conservative=proj["conservative"],
        base=proj["base"],
        aggressive=proj["aggressive"],
    ) + t("compliance_footer", lang)

    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def setdeposit(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    lang = user["language"]
    try:
        amount = float(ctx.args[0])
        assert 1 <= amount <= 10_000_000
    except (IndexError, ValueError, AssertionError):
        await update.message.reply_text(t("deposit_invalid", lang))
        return
    await pool.execute(
        "INSERT INTO user_copy_settings (user_id, deposit) VALUES ($1, $2) "
        "ON CONFLICT (user_id) DO UPDATE SET deposit = $2",
        user["id"], amount,
    )
    await update.message.reply_text(t("deposit_set", lang, deposit=amount))


async def setrisk(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    pool = await get_pool()
    user = await _get_or_create_user(pool, update.effective_user)
    lang = user["language"]
    try:
        risk = float(ctx.args[0])
        assert 0.1 <= risk <= 3.0
    except (IndexError, ValueError, AssertionError):
        await update.message.reply_text(t("risk_invalid", lang))
        return
    await pool.execute(
        "INSERT INTO user_copy_settings (user_id, risk_multiplier) VALUES ($1, $2) "
        "ON CONFLICT (user_id) DO UPDATE SET risk_multiplier = $2",
        user["id"], risk,
    )
    await update.message.reply_text(t("risk_set", lang, risk=risk))
