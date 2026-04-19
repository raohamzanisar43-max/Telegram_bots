"""
funded_bot/rules.py — Rule buffer logic and colour indicators for P3 Funded Bot

Colour indicators:
  🟢 Green  — < 50% of limit used
  🟡 Amber  — 50% – 80% of limit used
  🔴 Red    — > 80% of limit used
"""
from datetime import date
from shared.i18n import t


def _bar(used: float, limit: float) -> str:
    """Return colour indicator emoji based on % of limit consumed."""
    if limit == 0:
        return "⚫"
    ratio = used / limit
    if ratio < 0.5:
        return "🟢"
    elif ratio <= 0.8:
        return "🟡"
    else:
        return "🔴"


def build_status_message(account: dict, lang: str = "en") -> str:
    """Build the funded account status message with rule buffers."""
    current_gain      = float(account["current_gain"])
    profit_target     = float(account["profit_target"])
    used_daily_loss   = float(account["used_daily_loss"])
    max_daily_loss    = float(account["max_daily_loss"])
    used_overall_loss = float(account["used_overall_loss"])
    max_overall_loss  = float(account["max_overall_loss"])

    gain_bar    = _bar(current_gain,      profit_target)      # progress toward target
    daily_bar   = _bar(used_daily_loss,   max_daily_loss)
    overall_bar = _bar(used_overall_loss, max_overall_loss)

    msg = t(
        "funded_status", lang,
        date=date.today().strftime("%d %b %Y"),
        phase=account["phase"],
        account_size=float(account["account_size"]),
        current_gain=current_gain,
        profit_target=profit_target,
        gain_bar=gain_bar,
        used_daily_loss=used_daily_loss,
        max_daily_loss=max_daily_loss,
        daily_bar=daily_bar,
        used_overall_loss=used_overall_loss,
        max_overall_loss=max_overall_loss,
        overall_bar=overall_bar,
    ) + t("compliance_footer", lang)

    return msg
