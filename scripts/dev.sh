#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting ScrollIntel development environment..."

# Start backend
echo "🔧 Starting backend..."
uvicorn scrollintel.api.main:app --reload --port 6006 &

# Start frontend
echo "📦 Starting frontend..."
cd frontend
npm install
npm start &

# Wait for both processes
wait 