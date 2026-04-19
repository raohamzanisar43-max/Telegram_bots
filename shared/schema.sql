-- ─────────────────────────────────────────────────────────────────────────────
--  Profitability Intelligence — Database Schema
--  Do NOT modify without confirming with Ben first.
--  This schema is shared by all three bots.
-- ─────────────────────────────────────────────────────────────────────────────

-- ── Extensions ───────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Users (shared across all bots) ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              BIGSERIAL PRIMARY KEY,
    telegram_id     BIGINT      NOT NULL UNIQUE,
    username        VARCHAR(64),
    first_name      VARCHAR(128),
    language        CHAR(2)     NOT NULL DEFAULT 'en',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Subscriptions ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS subscriptions (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bot         VARCHAR(16) NOT NULL CHECK (bot IN ('signals', 'copy', 'funded')),
    active      BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, bot)
);

-- ── P1 — Signals ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS signals (
    id              BIGSERIAL PRIMARY KEY,
    channel_msg_id  BIGINT,
    direction       VARCHAR(4)  CHECK (direction IN ('BUY', 'SELL')),
    pair            VARCHAR(16),
    entry           NUMERIC(12, 5),
    sl              NUMERIC(12, 5),
    tp1             NUMERIC(12, 5),
    tp2             NUMERIC(12, 5),
    tp3             NUMERIC(12, 5),
    status          VARCHAR(16) NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'tp1', 'tp2', 'tp3', 'sl', 'be', 'partial', 'closed')),
    pips_result     NUMERIC(8, 1),
    raw_text        TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at       TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS signal_snapshots (
    id              BIGSERIAL PRIMARY KEY,
    snapshot_date   DATE        NOT NULL UNIQUE DEFAULT CURRENT_DATE,
    pips_closed     NUMERIC(8, 1) NOT NULL DEFAULT 0,
    pips_floating   NUMERIC(8, 1) NOT NULL DEFAULT 0,
    pips_week       NUMERIC(8, 1) NOT NULL DEFAULT 0,
    pips_month      NUMERIC(8, 1) NOT NULL DEFAULT 0,
    closed_count    INT         NOT NULL DEFAULT 0,
    open_count      INT         NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User lot size preferences (P1)
CREATE TABLE IF NOT EXISTS user_signals_settings (
    user_id     BIGINT  PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    lot_size    NUMERIC(6, 2) NOT NULL DEFAULT 0.10
);

-- ── P2 — Copy Bot ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS master_snapshots (
    id                  BIGSERIAL PRIMARY KEY,
    snapshot_ts         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    equity              NUMERIC(14, 2),
    balance             NUMERIC(14, 2),
    floating_pnl_pct    NUMERIC(8, 4),
    return_day_pct      NUMERIC(8, 4),
    return_week_pct     NUMERIC(8, 4),
    return_month_pct    NUMERIC(8, 4),
    drawdown_month      NUMERIC(8, 4),
    source              VARCHAR(8) NOT NULL DEFAULT 'api' CHECK (source IN ('api', 'manual'))
);

-- User copy settings
CREATE TABLE IF NOT EXISTS user_copy_settings (
    user_id         BIGINT  PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    deposit         NUMERIC(14, 2) NOT NULL DEFAULT 1000.00,
    risk_multiplier NUMERIC(4, 2)  NOT NULL DEFAULT 1.00,
    reinvest        BOOLEAN        NOT NULL DEFAULT TRUE
);

-- ── P3 — Funded Bot ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS funded_accounts (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             BIGINT      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_size        NUMERIC(14, 2) NOT NULL,
    profit_target       NUMERIC(6, 2)  NOT NULL,   -- % e.g. 10.00
    max_daily_loss      NUMERIC(6, 2)  NOT NULL,   -- % e.g. 5.00
    max_overall_loss    NUMERIC(6, 2)  NOT NULL,   -- % e.g. 10.00
    phase               VARCHAR(32)    NOT NULL DEFAULT 'challenge',
    current_gain        NUMERIC(6, 2)  NOT NULL DEFAULT 0,
    used_daily_loss     NUMERIC(6, 2)  NOT NULL DEFAULT 0,
    used_overall_loss   NUMERIC(6, 2)  NOT NULL DEFAULT 0,
    active              BOOLEAN        NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

-- ── Indexes ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_subscriptions_bot        ON subscriptions(bot, active);
CREATE INDEX IF NOT EXISTS idx_signals_status           ON signals(status);
CREATE INDEX IF NOT EXISTS idx_signal_snapshots_date    ON signal_snapshots(snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_master_snapshots_ts      ON master_snapshots(snapshot_ts DESC);
CREATE INDEX IF NOT EXISTS idx_funded_accounts_active   ON funded_accounts(active);
