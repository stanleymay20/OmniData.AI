#!/usr/bin/env python3
"""
Deployment script for OmniData.AI platform.
"""

import argparse
import logging
import os
import subprocess
import sys
import yaml
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Deployer:
    """Manages the deployment of OmniData.AI platform."""
    
    def __init__(self, config_path: str, environment: str):
        """Initialize deployer with configuration."""
        self.config_path = config_path
        self.environment = environment
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config['environments'][self.environment]
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            sys.exit(1)
    
    def _check_prerequisites(self) -> None:
        """Check if all prerequisites are met."""
        required_tools = ['docker', 'docker-compose']
        
        # Add kubectl requirement for non-development environments
        if self.environment != 'development':
            required_tools.append('kubectl')
        
        for tool in required_tools:
            try:
                subprocess.run([tool, '--version'], check=True, capture_output=True)
                logger.info(f"{tool} is available")
            except subprocess.CalledProcessError:
                logger.error(f"{tool} is required but not found")
                sys.exit(1)
    
    def _update_env_file(self) -> None:
        """Update environment variables file."""
        env_vars = {
            'ENVIRONMENT': self.environment,
            'API_HOST': self.config['api']['host'],
            'API_PORT': str(self.config['api']['port']),
            'DB_HOST': self.config['database']['host'],
            'DB_PORT': str(self.config['database']['port']),
            'DB_NAME': self.config['database']['name'],
            'DB_USER': os.getenv('DB_USER', self.config['database']['user']),
            'DB_PASSWORD': os.getenv('DB_PASSWORD', self.config['database']['password']),
            'MLFLOW_TRACKING_URI': os.getenv('MLFLOW_TRACKING_URI', self.config['mlflow']['tracking_uri']),
            'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'development-secret'),
            'SENTRY_DSN': os.getenv('SENTRY_DSN', '')
        }
        
        with open('.env', 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        logger.info("Environment file updated")
    
    def deploy(self) -> None:
        """Execute deployment process."""
        try:
            logger.info(f"Starting deployment for environment: {self.environment}")
            
            # Check prerequisites
            self._check_prerequisites()
            
            # Update environment variables
            self._update_env_file()
            
            # Build and deploy using docker-compose
            subprocess.run(
                ['docker-compose', 'build'],
                check=True
            )
            
            subprocess.run(
                ['docker-compose', 'up', '-d'],
                check=True
            )
            
            logger.info("Deployment completed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Deployment failed: {str(e)}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error during deployment: {str(e)}")
            sys.exit(1)
    
    def rollback(self) -> None:
        """Rollback deployment in case of failure."""
        try:
            logger.info("Initiating rollback")
            
            subprocess.run(
                ['docker-compose', 'down'],
                check=True
            )
            
            logger.info("Rollback completed successfully")
            
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            sys.exit(1)

def main():
    """Main entry point for deployment script."""
    parser = argparse.ArgumentParser(description='Deploy OmniData.AI platform')
    parser.add_argument(
        '--environment',
        choices=['development', 'staging', 'production'],
        default='development',
        help='Deployment environment'
    )
    parser.add_argument(
        '--config',
        default='deployment/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback deployment'
    )
    
    args = parser.parse_args()
    
    deployer = Deployer(args.config, args.environment)
    
    if args.rollback:
        deployer.rollback()
    else:
        deployer.deploy()

if __name__ == '__main__':
    main() 