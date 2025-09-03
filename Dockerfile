# Stage 1: Base image with dependencies
FROM python:3.11-slim AS base

WORKDIR /app

# Install system deps (if you ever need psycopg2, mysqlclient, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Stage 2: Final runtime image
FROM python:3.11-slim AS final

WORKDIR /app

# Copy installed dependencies from base
COPY --from=base /usr/local /usr/local

# Copy application code
COPY . .

# Expose container port
EXPOSE 8080

# Run with Gunicorn (production-ready WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
