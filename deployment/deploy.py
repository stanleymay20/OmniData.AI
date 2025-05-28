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
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(env):
    """Load configuration for the specified environment."""
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    if env not in config['environments']:
        raise ValueError(f"Environment {env} not found in config.yaml")
    
    return {**config['common'], **config['environments'][env]}

def setup_ssl(domain):
    """Set up SSL certificates using Let's Encrypt."""
    print(f"Setting up SSL for {domain}")
    subprocess.run([
        'certbot', 'certonly',
        '--standalone',
        '--agree-tos',
        '--non-interactive',
        '--domain', domain,
        '--email', os.getenv('ADMIN_EMAIL')
    ], check=True)

def update_env_file(config):
    """Update .env file with environment-specific values."""
    env_vars = {
        'DATABASE_URL': f"postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['name']}",
        'API_HOST': config['api']['host'],
        'API_PORT': config['api']['port'],
        'MLFLOW_TRACKING_URI': config['mlflow']['tracking_uri'],
        'PROMETHEUS_PORT': config['monitoring']['prometheus_port'],
        'GRAFANA_PORT': config['monitoring']['grafana_port']
    }
    
    with open('.env', 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

def deploy_services(config, env):
    """Deploy services using docker-compose."""
    compose_file = 'docker-compose.yml'
    if env != 'development':
        compose_file = f"deployment/docker-compose.{env}.yml"
    
    subprocess.run([
        'docker-compose',
        '-f', compose_file,
        'up',
        '-d',
        '--build'
    ], check=True)

def setup_monitoring():
    """Set up monitoring tools."""
    subprocess.run([
        'docker-compose',
        '-f', 'deployment/monitoring.yml',
        'up',
        '-d'
    ], check=True)

def verify_deployment(config):
    """Verify the deployment is working."""
    health_check = subprocess.run([
        'python',
        'deployment/healthcheck.py',
        '--host', config['api']['host'],
        '--port', str(config['api']['port'])
    ])
    return health_check.returncode == 0

def main():
    parser = argparse.ArgumentParser(description='Deploy OmniData.AI services')
    parser.add_argument('--env', choices=['development', 'staging', 'production'],
                      default='development', help='Deployment environment')
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.env)
        print(f"Deploying to {args.env} environment")

        # Update environment variables
        update_env_file(config)
        print("Updated environment variables")

        # Set up SSL for non-development environments
        if args.env != 'development':
            setup_ssl(config['api']['host'])
            print("SSL certificates configured")

        # Deploy services
        deploy_services(config, args.env)
        print("Services deployed")

        # Set up monitoring
        setup_monitoring()
        print("Monitoring configured")

        # Verify deployment
        if verify_deployment(config):
            print("Deployment verified successfully")
        else:
            print("Deployment verification failed", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Deployment failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 