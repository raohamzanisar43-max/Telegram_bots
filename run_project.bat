@echo off
echo Starting Profitability Intelligence Project...
echo.

echo 1. Starting Signals Bot...
start "Signals Bot" cmd /k "set PYTHONPATH=. && python signals_bot/main.py"

echo 2. Starting Admin API...
start "Admin API" cmd /k "set PYTHONPATH=. && python admin/main.py"

echo.
echo Project started! Check the opened windows for status.
echo.
echo Bot Commands:
echo - Send /start to @hamzaaautomaiton_bot
echo - Admin API: http://localhost:4000/health
echo.
pause
