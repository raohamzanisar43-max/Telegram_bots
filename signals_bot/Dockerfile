FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY signals_bot/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared package and bot code
COPY shared/ ./shared/
COPY signals_bot/ ./signals_bot/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "signals_bot.main"]
