FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/ai_service \
    HF_HOME=/home/appuser/.cache/huggingface \
    PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /home/appuser/.cache/huggingface \
    && chown -R appuser:appuser /home/appuser

COPY --chown=appuser:appuser \
    ai_service/requirements.txt \
    /app/ai_service/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        torch \
    && python -c "import torch; print('torch==' + torch.__version__)" \
        > /tmp/torch-constraints.txt \
    && python -m pip install --no-cache-dir \
        --index-url https://pypi.org/simple \
        -c /tmp/torch-constraints.txt \
        -r /app/ai_service/requirements.txt \
    && rm /tmp/torch-constraints.txt

COPY --chown=appuser:appuser ai_service /app/ai_service

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --app-dir /app/ai_service --host 0.0.0.0 --port ${PORT:-8000}"]

