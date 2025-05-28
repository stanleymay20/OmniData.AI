"""
Database initialization script for OmniData.AI
"""

import os
import time
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables."""
    return (
        f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@"
        f"{os.getenv('DB_HOST', 'db')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'omnidata')}"
    )

def wait_for_db(max_retries=30, retry_interval=2):
    """Wait for the database to be ready."""
    logger.info("Waiting for database to be ready...")
    
    for i in range(max_retries):
        try:
            engine = create_engine(get_database_url())
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database is ready!")
                return True
        except OperationalError:
            logger.info(f"Database not ready yet. Retrying in {retry_interval} seconds... ({i+1}/{max_retries})")
            time.sleep(retry_interval)
    
    logger.error("Database connection failed after maximum retries.")
    return False

def init_db():
    """Initialize the database with required tables."""
    if not wait_for_db():
        return False
    
    engine = create_engine(get_database_url())
    
    # Create tables
    with engine.connect() as conn:
        # Create users table
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        
        # Create api_keys table
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            service VARCHAR(50) NOT NULL,
            key_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
        """))
        
        # Create models table
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS models (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            model_type VARCHAR(50) NOT NULL,
            parameters JSONB,
            metrics JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        
        # Create datasets table
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS datasets (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            source VARCHAR(200) NOT NULL,
            schema JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        
        conn.commit()
    
    logger.info("Database initialized successfully!")
    return True

if __name__ == "__main__":
    init_db() 