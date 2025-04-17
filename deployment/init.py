#!/usr/bin/env python3
"""
Initialization script for OmniData.AI deployment.
"""

import os
import sys
import time
import logging
import subprocess
import psutil
from typing import Optional

# Configure logging with more verbose output
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG level
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentInitializer:
    def __init__(self):
        self.max_retries = 5
        self.retry_interval = 10  # seconds
        logger.info("Initializing deployment process...")

    def check_docker_running(self) -> bool:
        """Check if Docker is running."""
        logger.debug("Checking Docker status...")
        try:
            result = subprocess.run(['docker', 'info'], check=True, capture_output=True, text=True)
            logger.debug(f"Docker info output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker check failed: {str(e)}")
            logger.debug(f"Error output: {e.stderr}")
            return False

    def wait_for_docker(self, timeout: int = 300) -> bool:
        """Wait for Docker to be ready."""
        logger.info("Waiting for Docker to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.check_docker_running():
                logger.info("Docker is ready!")
                return True
            
            logger.info("Docker not ready yet, waiting...")
            time.sleep(10)
        
        logger.error(f"Docker did not become ready within {timeout} seconds")
        return False

    def verify_environment(self) -> bool:
        """Verify environment variables and configurations."""
        logger.info("Verifying environment variables...")
        required_vars = [
            'ENVIRONMENT',
            'API_HOST',
            'API_PORT',
            'DB_HOST',
            'DB_PORT',
            'DB_NAME',
            'DB_USER',
            'DB_PASSWORD',
            'JWT_SECRET_KEY'
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                logger.debug(f"Found {var}={value}")
            else:
                logger.error(f"Missing required environment variable: {var}")
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        logger.info("Environment verification completed successfully")
        return True

    def create_directories(self) -> None:
        """Create necessary directories for deployment."""
        logger.info("Creating necessary directories...")
        directories = [
            'data',
            'logs',
            'models',
            'temp'
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {str(e)}")
                raise

    def check_ports_available(self) -> bool:
        """Check if required ports are available."""
        logger.info("Checking port availability...")
        required_ports = [8000, 8501, 5432, 5000, 8080, 9090, 3000]
        
        for port in required_ports:
            if self.is_port_in_use(port):
                logger.error(f"Port {port} is already in use")
                return False
            logger.debug(f"Port {port} is available")
        
        logger.info("All required ports are available")
        return True

    @staticmethod
    def is_port_in_use(port: int) -> bool:
        """Check if a port is in use."""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking port {port}: {str(e)}")
            return True  # Assume port is in use if we can't check

    def initialize(self) -> bool:
        """Run the complete initialization process."""
        logger.info("Starting initialization process...")
        try:
            # Step 1: Wait for Docker
            if not self.wait_for_docker():
                logger.error("Docker failed to start")
                return False

            # Step 2: Verify environment
            if not self.verify_environment():
                logger.error("Environment verification failed")
                return False

            # Step 3: Check ports
            if not self.check_ports_available():
                logger.error("Required ports are not available")
                return False

            # Step 4: Create directories
            self.create_directories()

            logger.info("Initialization completed successfully")
            return True

        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            logger.debug("Stack trace:", exc_info=True)
            return False

def main():
    """Main entry point."""
    try:
        logger.info("Starting deployment initialization...")
        initializer = DeploymentInitializer()
        
        if initializer.initialize():
            logger.info("System is ready for deployment")
            sys.exit(0)
        else:
            logger.error("System is not ready for deployment")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Deployment initialization failed: {str(e)}")
        logger.debug("Stack trace:", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main() 