#!/usr/bin/env python3
"""
Health check script for OmniData.AI platform services.
"""

import argparse
import logging
import requests
import sys
import time
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_service(url: str, timeout: int = 5) -> bool:
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_services(services: Dict[str, str], max_retries: int = 5, retry_delay: int = 10) -> List[str]:
    failed_services = []
    for name, url in services.items():
        print(f"Checking {name} at {url}...")
        for attempt in range(max_retries):
            if check_service(url):
                print(f"✓ {name} is healthy")
                break
            if attempt < max_retries - 1:
                print(f"✗ {name} not ready, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"✗ {name} failed health check")
                failed_services.append(name)
    return failed_services

def main():
    """Main entry point for health check script."""
    parser = argparse.ArgumentParser(description='Health check for OmniData.AI services')
    parser.add_argument('--host', default='localhost', help='Host to check')
    parser.add_argument('--port', type=int, default=8000, help='Port to check')
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"
    services = {
        'Frontend': f"{base_url}:8501",
        'Backend API': f"{base_url}/health",
        'Grafana': f"{base_url}:3000",
        'Prometheus': f"{base_url}:9090/-/healthy"
    }

    failed_services = check_services(services)
    if failed_services:
        print(f"\nFailed services: {', '.join(failed_services)}")
        sys.exit(1)
    else:
        print("\nAll services are healthy!")

if __name__ == '__main__':
    main() 