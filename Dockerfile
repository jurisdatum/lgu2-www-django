# ==========================================
# STAGE 1: Builder
# ==========================================
FROM python:3.12.12-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# 1. Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Extract requirements (Cached unless pyproject.toml changes)
RUN pip install --no-cache-dir poetry==1.8.4 poetry-plugin-export
COPY pyproject.toml poetry.lock ./
RUN poetry export --without dev -f requirements.txt --output requirements.txt

# 3. Build Wheels (Cached unless requirements.txt changes)
RUN pip wheel --wheel-dir /wheels -r requirements.txt

# 4. Install dependencies in Builder (Cached unless requirements.txt changes)
# We install here specifically so we can run collectstatic later.
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# 5. Copy Source Code (This changes frequently, so it goes last)
COPY . /app

# 6. Collect Static (Runs only after code copy)
RUN SECRET_KEY=dummy DEBUG=True USE_WHITENOISE=True \
    python manage.py collectstatic --noinput

# ==========================================
# STAGE 2: Final Runtime
# ==========================================
FROM python:3.12.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN useradd -m -u 10001 appuser

# 7. Install Python Dependencies from Wheels
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r /app/requirements.txt \
    && rm -rf /wheels

# 8. Copy Application Code & Assets
# COPY --from=builder /app/manage.py /app/manage.py
COPY --from=builder /app/lgu2 /app/lgu2
COPY --from=builder /app/staticfiles /app/staticfiles
COPY --from=builder /app/gunicorn.conf.py /app/gunicorn.conf.py

USER appuser
EXPOSE 8000

ENV PORT=8000 \
    WEB_CONCURRENCY=2 \
    GUNICORN_TIMEOUT=30 \
    USE_WHITENOISE=True \
    CACHE_LOCATION=/tmp/django_cache

CMD ["gunicorn", "-c", "gunicorn.conf.py", "lgu2.wsgi:application"]
