FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHROMA_PERSIST_DIR=/app/chroma_db \
    BM25_PERSIST_PATH=/tmp/bm25_index.pkl \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel && \
    pip --no-cache-dir install -r /app/requirements.txt

    RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

RUN useradd --create-home appuser && chown -R appuser:appuser /app
RUN mkdir -p /app/chroma_db && chown -R appuser:appuser /app/chroma_db

USER appuser

COPY --chown=appuser:appuser . /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "--nothreading", "0.0.0.0:8000"]