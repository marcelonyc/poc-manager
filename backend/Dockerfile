FROM python:3.11-slim
ARG USER_ID=${USER_ID:-1000}
ARG GROUP_ID=${GROUP_ID:-1000}
RUN addgroup --gid ${GROUP_ID} appuser && \
    adduser -u ${USER_ID} --disabled-password --gid ${GROUP_ID} appuser

WORKDIR /app
RUN chown appuser:appuser /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install as root so binaries land on PATH
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Suppress external dependency deprecation warnings that don't affect functionality
ENV PYTHONWARNINGS="ignore:.*crypt.*:"

# Run the application
CMD ["uvicorn", "app.main:combined_app", "--host", "0.0.0.0", "--port", "8000"]
