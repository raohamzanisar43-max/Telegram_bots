@echo off
echo Adding Funded Bot token...

(
echo # ─────────────────────────────────────────────
echo #  Profitability Intelligence — Environment File
echo #  Copy to .env and fill in all REPLACE_WITH_... values
echo #  NEVER commit .env to git
echo # ─────────────────────────────────────────────
echo.
echo # ── Telegram Bot Tokens ^(create via @BotFather^) ──
echo SIGNALS_BOT_TOKEN=8649263884:AAF5l0OPBVJNEALBb-kgGkOe_RN44Ad-ydI
echo COPY_BOT_TOKEN=8693180078:AAEZMjvDYUAmp4yfiYw5WMoFUrwxPJ6uE0w
echo FUNDED_BOT_TOKEN=8682152900:AAHnn4nGlzwNK_YIi-9n7N32hiuD0U9DpPE
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

echo Funded Bot token added successfully!
echo.
echo Starting Funded Bot...
powershell -ExecutionPolicy Bypass -Command "$env:PYTHONPATH='.'; python funded_bot/main.py"
pause
