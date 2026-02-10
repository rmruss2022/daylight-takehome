# Multi-stage build
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 django && chown -R django:django /app
USER django

# Expose port
EXPOSE 8000

# Copy all entrypoint scripts
COPY --chown=django:django entrypoint.sh /app/
COPY --chown=django:django smart-entrypoint.sh /app/
COPY --chown=django:django railway-celery-worker.sh /app/
COPY --chown=django:django railway-celery-beat.sh /app/
RUN chmod +x /app/entrypoint.sh /app/smart-entrypoint.sh /app/railway-celery-worker.sh /app/railway-celery-beat.sh

# Default command
CMD ["bash", "/app/smart-entrypoint.sh"]
