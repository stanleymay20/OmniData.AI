#!/bin/bash

# Exit on error
set -e

echo "🚀 Deploying ScrollIntel..."

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Build backend
echo "🔧 Building backend..."
docker-compose build

# Deploy to EC2
echo "☁️ Deploying to EC2..."
ssh -i ~/.ssh/scrollintel.pem ec2-user@your-ec2-instance << 'ENDSSH'
  cd /home/ec2-user/scrollintel
  git pull origin main
  docker-compose down
  docker-compose up -d
ENDSSH

echo "✅ Deployment complete!" 