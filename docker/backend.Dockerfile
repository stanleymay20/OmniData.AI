# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=0 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with retry mechanism
RUN pip install --no-cache-dir -r requirements.txt || \
    (pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt) || \
    (pip install --no-cache-dir --no-deps -r requirements.txt && pip install --no-cache-dir -r requirements.txt)

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "omnidata.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 