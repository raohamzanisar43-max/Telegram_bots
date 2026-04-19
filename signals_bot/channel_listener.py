"""
signals_bot/channel_listener.py — Listens to VIP channel posts and parses signals
"""
import re
from telegram import Update
from telegram.ext import ContextTypes

from shared.db import get_pool
from shared.logger import get_logger

logger = get_logger("signals-bot")

# ── Signal Parser ─────────────────────────────────────────────────────────────

_SIGNAL_RE = re.compile(
    r"(?P<direction>BUY|SELL)\s+(?P<pair>[A-Z]{3,10}(?:[/_][A-Z]{2,6})?)",
    re.IGNORECASE,
)
_ENTRY_RE  = re.compile(r"entry[:\s]+([0-9]+\.?[0-9]*)", re.IGNORECASE)
_SL_RE     = re.compile(r"s[lt][:\s]+([0-9]+\.?[0-9]*)", re.IGNORECASE)
_TP_RE     = re.compile(r"tp\s*([123]?)[:\s]+([0-9]+\.?[0-9]*)", re.IGNORECASE)

# Status update patterns
_TP_HIT_RE   = re.compile(r"tp\s*([123]?)\s*(hit|closed|reached)", re.IGNORECASE)
_SL_HIT_RE   = re.compile(r"sl\s*(hit|closed|triggered)", re.IGNORECASE)
_BE_RE       = re.compile(r"\bB[./]?E\b|break[\s-]?even", re.IGNORECASE)
_PARTIAL_RE  = re.compile(r"partial\s*(close|profit)", re.IGNORECASE)


def parse_signal(text: str) -> dict | None:
    """Try to parse a new signal from channel message text. Returns dict or None."""
    m = _SIGNAL_RE.search(text)
    if not m:
        return None

    entry_m = _ENTRY_RE.search(text)
    sl_m    = _SL_RE.search(text)
    tps = {int(g or 1): float(v) for g, v in _TP_RE.findall(text)}

    return {
        "direction": m.group("direction").upper(),
        "pair":      m.group("pair").upper().replace("/", ""),
        "entry":     float(entry_m.group(1)) if entry_m else None,
        "sl":        float(sl_m.group(1))    if sl_m    else None,
        "tp1":       tps.get(1),
        "tp2":       tps.get(2),
        "tp3":       tps.get(3),
    }


def parse_status_update(text: str) -> dict | None:
    """Try to parse a status update (TP hit / SL / BE / partial)."""
    if _TP_HIT_RE.search(text):
        m = _TP_HIT_RE.search(text)
        lvl = int(m.group(1)) if m.group(1) else 1
        return {"status": f"tp{lvl}"}
    if _SL_HIT_RE.search(text):
        return {"status": "sl"}
    if _BE_RE.search(text):
        return {"status": "be"}
    if _PARTIAL_RE.search(text):
        return {"status": "partial"}
    return None


# ── Handler ───────────────────────────────────────────────────────────────────

async def channel_post_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.channel_post
    if not msg or not msg.text:
        return

    text = msg.text
    pool = await get_pool()

    # Try new signal first
    signal = parse_signal(text)
    if signal:
        await pool.execute(
            """
            INSERT INTO signals
                (channel_msg_id, direction, pair, entry, sl, tp1, tp2, tp3, status, raw_text)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'open', $9)
            """,
            msg.message_id,
            signal["direction"],
            signal["pair"],
            signal["entry"],
            signal["sl"],
            signal["tp1"],
            signal["tp2"],
            signal["tp3"],
            text[:1000],
        )
        logger.info(f"Stored signal: {signal['direction']} {signal['pair']}")
        return

    # Try status update
    status = parse_status_update(text)
    if status:
        # Update the most recent open signal (best-effort matching)
        row = await pool.fetchrow(
            "SELECT id FROM signals WHERE status = 'open' ORDER BY created_at DESC LIMIT 1"
        )
        if row:
            await pool.execute(
                "UPDATE signals SET status = $1, closed_at = NOW() WHERE id = $2",
                status["status"], row["id"],
            )
            logger.info(f"Updated signal {row['id']} → {status['status']}")
