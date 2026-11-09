FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    PORT=8501

WORKDIR /app

RUN useradd --create-home --uid 10001 appuser

COPY streamlit_app/requirements.txt /app/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install \
        --no-cache-dir \
        --retries 5 \
        --timeout 120 \
        --index-url https://pypi.org/simple \
        -r /app/requirements.txt 

COPY --chown=appuser:appuser streamlit_app /app

USER appuser

EXPOSE 8501

CMD ["sh", "-c", "streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"] 