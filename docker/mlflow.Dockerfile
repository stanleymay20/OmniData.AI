# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install MLflow
RUN pip install --no-cache-dir \
    mlflow>=2.8.0 \
    psycopg2-binary>=2.9.9 \
    boto3>=1.28.0

# Create directories for artifacts
RUN mkdir -p /app/mlruns

# Expose port
EXPOSE 5000

# Start MLflow tracking server
CMD ["mlflow", "server", \
    "--host", "0.0.0.0", \
    "--port", "5000", \
    "--backend-store-uri", "${MLFLOW_TRACKING_URI}", \
    "--default-artifact-root", "/app/mlruns"] 