"""
copy_bot/compounding.py — Compounding engine and 12-month projection calculator
"""
from __future__ import annotations


def compound_balance(
    start_balance: float,
    daily_pct: float,
    days: int,
    reinvest: bool = True,
) -> float:
    """
    Compound a balance over N days.
    If reinvest=False, treat as simple interest (daily_pct applied to start only).
    """
    if reinvest:
        return start_balance * ((1 + daily_pct / 100) ** days)
    else:
        return start_balance * (1 + (daily_pct / 100) * days)


def apply_risk(daily_pct: float, risk_multiplier: float) -> float:
    """Scale the daily return by the user's risk multiplier."""
    return daily_pct * risk_multiplier


def generate_projection(
    deposit: float,
    monthly_pct: float,
    risk_multiplier: float = 1.0,
    reinvest: bool = True,
    months: int = 12,
) -> dict:
    """
    Generate conservative / base / aggressive 12-month projections.

    Scenarios:
        conservative = 0.6x of base monthly return
        base         = 1.0x
        aggressive   = 1.4x

    Returns a dict with 'conservative', 'base', 'aggressive' final balances
    and a 'monthly' list of dicts for each month (all three scenarios).
    """
    MULTIPLIERS = {
        "conservative": 0.6,
        "base":         1.0,
        "aggressive":   1.4,
    }

    results: dict = {k: [] for k in MULTIPLIERS}
    balances = {k: deposit for k in MULTIPLIERS}

    for month in range(1, months + 1):
        for scenario, factor in MULTIPLIERS.items():
            effective_pct = monthly_pct * risk_multiplier * factor
            if reinvest:
                balances[scenario] *= (1 + effective_pct / 100)
            else:
                balances[scenario] += deposit * (effective_pct / 100)
            results[scenario].append(round(balances[scenario], 2))

    return {
        "conservative": round(balances["conservative"], 2),
        "base":         round(balances["base"], 2),
        "aggressive":   round(balances["aggressive"], 2),
        "monthly":      [
            {
                "month":        m + 1,
                "conservative": results["conservative"][m],
                "base":         results["base"][m],
                "aggressive":   results["aggressive"][m],
            }
            for m in range(months)
        ],
    }


def user_balance_today(
    deposit: float,
    daily_pct: float,
    risk_multiplier: float,
    reinvest: bool,
) -> float:
    """
    Apply today's master return to a user's deposit with their risk settings.
    Used for the personalised daily report.
    """
    effective_pct = apply_risk(daily_pct, risk_multiplier)
    return compound_balance(deposit, effective_pct, days=1, reinvest=reinvest)
