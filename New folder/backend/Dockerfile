FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

ENV ML_MODEL_PATH=/app/ml/artifacts/model.pkl
ENV ML_METRICS_PATH=/app/ml/artifacts/metrics.json
# Mount ml/artifacts at runtime (see docker-compose.yml)

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
