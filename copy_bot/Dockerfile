FROM python:3.12-slim

WORKDIR /app

COPY copy_bot/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY copy_bot/ ./copy_bot/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "copy_bot.main"]
