# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scrollintel/ ./scrollintel/
COPY frontend/ ./frontend/

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=6006

# Expose port
EXPOSE 6006

# Create launch script
COPY launch.sh .
RUN chmod +x launch.sh

# Run the application
CMD ["./launch.sh"] 