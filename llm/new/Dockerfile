FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TESSERACT_CMD=/usr/bin/tesseract \
    CHROMA_PERSIST_DIR=/app/chroma_db \
    BM25_PERSIST_PATH=/tmp/bm25_index.pkl \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      poppler-utils \
      tesseract-ocr \
      libtesseract-dev \
      && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel && \
    pip --no-cache-dir install -r /app/requirements.txt && \
    python -c "import nltk; nltk.download('punkt')"

RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

COPY --chown=appuser:appuser . /app

RUN mkdir -p /app/chroma_db /tmp && \
    chown -R appuser:appuser /app/chroma_db /tmp

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "--nothreading", "0.0.0.0:8000"]