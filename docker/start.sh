#!/bin/bash
set -e

# Initialize the database
echo "Initializing database..."
python -m omnidata.database.init_db

# Start the application
echo "Starting OmniData.AI backend..."
exec uvicorn omnidata.api.main:app --host 0.0.0.0 --port 8000 --reload 