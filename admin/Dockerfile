FROM python:3.12-slim

WORKDIR /app

COPY admin/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY admin/ ./admin/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "admin.main:app", "--host", "0.0.0.0", "--port", "4000"]
