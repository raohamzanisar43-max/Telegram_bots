@echo off
echo Updating .env file with correct configuration...

(
echo # ─────────────────────────────────────────────
echo #  Profitability Intelligence — Environment File
echo #  Copy to .env and fill in all REPLACE_WITH_... values
echo #  NEVER commit .env to git
echo # ─────────────────────────────────────────────
echo.
echo # ── Telegram Bot Tokens ^(create via @BotFather^) ──
echo SIGNALS_BOT_TOKEN=8649263884:AAFPqrFae-ZaXp6M79NPKC_LlAdbKKAS_bU
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

echo .env file updated successfully!
echo.
echo Configuration values set:
echo - SIGNALS_BOT_TOKEN: 8649263884:AAFPqrFae-ZaXp6M79NPKC_LlAdbKKAS_bU
echo - POSTGRES_HOST: localhost
echo - POSTGRES_PORT: 5432
echo - POSTGRES_DB: postgres
echo - POSTGRES_USER: postgres
echo - POSTGRES_PASSWORD: admin123
echo - SIGNALS_VIP_CHANNEL_ID: -1000000000000
echo.
echo You can now start the bot with: python signals_bot/main.py
pause
