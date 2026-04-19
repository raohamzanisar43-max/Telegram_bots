FROM python:3.12-slim

WORKDIR /app

COPY funded_bot/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY funded_bot/ ./funded_bot/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "funded_bot.main"]
