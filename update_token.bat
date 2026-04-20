@echo off
echo Updating bot token...

(
echo # ─────────────────────────────────────────────
echo #  Profitability Intelligence — Environment File
echo #  Copy to .env and fill in all REPLACE_WITH_... values
echo #  NEVER commit .env to git
echo # ─────────────────────────────────────────────
echo.
echo # ── Telegram Bot Tokens ^(create via @BotFather^) ──
echo SIGNALS_BOT_TOKEN=8649263884:AAF5l0OPBVJNEALBb-kgGkOe_RN44Ad-ydI
echo COPY_BOT_TOKEN=REPLACE_WITH_COPY_BOT_TOKEN
echo FUNDED_BOT_TOKEN=REPLACE_WITH_FUNDED_BOT_TOKEN
echo.
echo # ── VIP Channel ^(negative number, e.g. -1001234567890^) ──
echo SIGNALS_VIP_CHANNEL_ID=-1000000000000
echo.
echo # ── MetaAPI ^(from app.metaapi.cloud dashboard^) ──
echo META_API_TOKEN=REPLACE_WITH_META_API_TOKEN
echo MT4_ACCOUNT_ID=REPLACE_WITH_MT4_ACCOUNT_ID
echo.
echo # ── PostgreSQL ──
echo POSTGRES_HOST=localhost
echo POSTGRES_PORT=5432
echo POSTGRES_DB=postgres
echo POSTGRES_USER=postgres
echo POSTGRES_PASSWORD=admin123
echo.
echo # ── Redis ──
echo REDIS_HOST=localhost
echo REDIS_PORT=6379
echo.
echo # ── Admin API ──
echo ADMIN_SECRET=REPLACE_WITH_STRONG_RANDOM_SECRET
echo.
echo # ── General ──
echo LOG_LEVEL=INFO
echo TZ=UTC
) > .env

echo Token updated successfully!
echo New token: 8649263884:AAF5l0OPBVJNEALBb-kgGkOe_RN44Ad-ydI
echo.
echo Starting bot with new token...
powershell -ExecutionPolicy Bypass -File start_bot.ps1
pause
