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

class HealthChecker:
    """Monitors health of OmniData.AI services."""
    
    def __init__(
        self,
        api_url: str,
        frontend_url: str,
        db_url: str,
        mlflow_url: str,
        airflow_url: str
    ):
        """Initialize health checker with service URLs."""
        self.services = {
            'api': api_url,
            'frontend': frontend_url,
            'database': db_url,
            'mlflow': mlflow_url,
            'airflow': airflow_url
        }
    
    def check_service(self, service: str, url: str) -> Dict[str, str]:
        """Check health of a specific service."""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            response.raise_for_status()
            
            return {
                'service': service,
                'status': 'healthy',
                'latency': f"{response.elapsed.total_seconds() * 1000:.2f}ms"
            }
            
        except requests.RequestException as e:
            return {
                'service': service,
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_all_services(self) -> List[Dict[str, str]]:
        """Check health of all services."""
        results = []
        
        for service, url in self.services.items():
            result = self.check_service(service, url)
            results.append(result)
            
            if result['status'] == 'unhealthy':
                logger.warning(f"{service} is unhealthy: {result.get('error')}")
            else:
                logger.info(f"{service} is healthy (latency: {result['latency']})")
        
        return results
    
    def monitor(
        self,
        interval: int = 60,
        max_failures: Optional[int] = None
    ) -> None:
        """Continuously monitor services."""
        failure_count = 0
        
        while True:
            unhealthy_services = []
            results = self.check_all_services()
            
            for result in results:
                if result['status'] == 'unhealthy':
                    unhealthy_services.append(result['service'])
            
            if unhealthy_services:
                failure_count += 1
                logger.error(f"Unhealthy services detected: {', '.join(unhealthy_services)}")
                
                if max_failures and failure_count >= max_failures:
                    logger.critical(f"Maximum failures ({max_failures}) reached")
                    sys.exit(1)
            else:
                failure_count = 0
                logger.info("All services are healthy")
            
            time.sleep(interval)

def main():
    """Main entry point for health check script."""
    parser = argparse.ArgumentParser(description='Monitor OmniData.AI services')
    parser.add_argument(
        '--api-url',
        default='http://localhost:8000',
        help='API service URL'
    )
    parser.add_argument(
        '--frontend-url',
        default='http://localhost:8501',
        help='Frontend service URL'
    )
    parser.add_argument(
        '--db-url',
        default='http://localhost:5432',
        help='Database service URL'
    )
    parser.add_argument(
        '--mlflow-url',
        default='http://localhost:5000',
        help='MLflow service URL'
    )
    parser.add_argument(
        '--airflow-url',
        default='http://localhost:8080',
        help='Airflow service URL'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Monitoring interval in seconds'
    )
    parser.add_argument(
        '--max-failures',
        type=int,
        help='Maximum number of consecutive failures before exit'
    )
    
    args = parser.parse_args()
    
    checker = HealthChecker(
        api_url=args.api_url,
        frontend_url=args.frontend_url,
        db_url=args.db_url,
        mlflow_url=args.mlflow_url,
        airflow_url=args.airflow_url
    )
    
    checker.monitor(
        interval=args.interval,
        max_failures=args.max_failures
    )

if __name__ == '__main__':
    main() 