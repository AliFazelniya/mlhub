# ---- Base image ----
FROM python:3.11-slim

# ---- Environment ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    TESSERACT_CMD=/usr/bin/tesseract \
    CHROMA_PERSIST_DIR=/app/chroma_db \
    BM25_PERSIST_PATH=/tmp/bm25_index.pkl \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /app

# ---- system dependencies for OCR, pdf2image, and common libs ----
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      git \
      curl \
      ca-certificates \
      wget \
      gcc \
      poppler-utils \          # required by pdf2image
      tesseract-ocr \          # Tesseract binary
      libtesseract-dev \
      libgl1 \                 # required by some image libs / torch vision
      libsm6 \
      libxrender1 \
      libffi-dev \
      libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# ---- Copy requirements early for layer caching ----
COPY requirements.txt /app/requirements.txt

# Upgrade pip and install Python deps (non-cached)
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip --no-cache-dir install -r /app/requirements.txt

# Download NLTK punkt tokenizer (used by BM25 index)
RUN python -c "import nltk; nltk.download('punkt')"

# ---- Create a non-root user ----
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# ---- Copy project files (as non-root user) ----
COPY --chown=appuser:appuser . /app

# Create persistent directories and ensure ownership
RUN mkdir -p /app/chroma_db /tmp && \
    chown -R appuser:appuser /app/chroma_db /tmp

# Expose port (adjust if you run via different port)
EXPOSE 8000

# ---- Entrypoint and CMD ----
# Wait-for-db scripts or migrations can be added here. Use environment variables to configure Django settings.
ENV DJANGO_SETTINGS_MODULE=config.settings
# Collectstatic skipped by default; run collectstatic in your deployment pipeline if needed.

# By default run gunicorn; adjust worker count for your environment.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "4", "--timeout", "120"]