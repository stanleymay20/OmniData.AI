#!/bin/bash

# Start the FastAPI backend
uvicorn scrollintel.api.main:app --host 0.0.0.0 --port $PORT &

# Start the frontend
cd frontend && npm install && npm start &

# Keep container running
tail -f /dev/null 