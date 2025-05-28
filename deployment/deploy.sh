#!/bin/bash

# Exit on error
set -e

# Load environment variables
source .env

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."
for cmd in docker docker-compose python3 aws; do
    if ! command_exists $cmd; then
        echo "Error: $cmd is required but not installed"
        exit 1
    fi
done

# Build and start services
echo "Building and starting services..."
docker-compose build
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Run database migrations
echo "Running database migrations..."
python deployment/migrate.py --env production

# Set up monitoring
echo "Setting up monitoring..."
docker-compose -f deployment/monitoring.yml up -d

# Create initial backup
echo "Creating initial backup..."
python deployment/backup.py --action backup --service all

# Upload backup to S3
echo "Uploading backup to S3..."
aws s3 sync backups/ s3://omnidata-backups/$(date +%Y%m%d)/

# Verify deployment
echo "Verifying deployment..."
python deployment/healthcheck.py --host localhost --port 8000

# Set up SSL if in production
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Setting up SSL..."
    python deployment/deploy.py --env production
fi

echo "Deployment completed successfully!"
echo "Services are running at:"
echo "- Frontend: http://localhost:8501"
echo "- Backend API: http://localhost:8000"
echo "- Grafana: http://localhost:3000"
echo "- Prometheus: http://localhost:9090" 