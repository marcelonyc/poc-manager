# ── Stage 1: Build dependencies ──
FROM python:3.11-slim AS builder

ARG PIP_TRUSTED_HOST
ARG PIP_INDEX_URL
ENV PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST}
ENV PIP_INDEX_URL=${PIP_INDEX_URL}

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Production image ──
FROM python:3.11-slim

ARG VERSION=latest
LABEL org.opencontainers.image.version="${VERSION}"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Ensure uploads directory exists for volume mount
RUN mkdir -p /app/uploads

EXPOSE 8000

ENV PYTHONWARNINGS="ignore:.*crypt.*:" \
    PYTHONUNBUFFERED=1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:combined_app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
