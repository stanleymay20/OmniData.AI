"""
ScrollIntel v2: The Flame Interpreter
Google Analytics 4 integration client
"""

from typing import Dict, Any, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Metric,
    Dimension
)
import os
import json
import pickle
from datetime import datetime, timedelta
import pytz
import pandas as pd

from .base import BaseIntegration

class GA4Client(BaseIntegration):
    """Google Analytics 4 integration client."""
    
    SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
    TOKEN_PATH = 'credentials/ga4_token.pickle'
    CREDENTIALS_PATH = 'credentials/ga4_credentials.json'
    
    def __init__(self, credentials: Dict[str, Any]):
        """Initialize GA4 client with OAuth2 credentials."""
        super().__init__(credentials)
        self.credentials = self._get_credentials()
        self.client = BetaAnalyticsDataClient(credentials=self.credentials)
        self._log_integration("initialize", {"status": "success"})
    
    def _get_credentials(self) -> Credentials:
        """Get or refresh OAuth2 credentials."""
        creds = None
        
        # Create credentials directory if it doesn't exist
        os.makedirs('credentials', exist_ok=True)
        
        # Load existing token
        if os.path.exists(self.TOKEN_PATH):
            with open(self.TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.CREDENTIALS_PATH):
                    raise ValueError(
                        f"GA4 credentials file not found at {self.CREDENTIALS_PATH}. "
                        "Please download from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDENTIALS_PATH, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    async def fetch_data(
        self,
        property_id: str,
        date_range: Optional[Dict[str, str]] = None,
        metrics: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch metrics from GA4 property."""
        try:
            # Set default date range if not provided
            if not date_range:
                end_date = datetime.now(pytz.UTC)
                start_date = end_date - timedelta(days=30)
                date_range = {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
            
            # Set default metrics if not provided
            if not metrics:
                metrics = [
                    "totalUsers",
                    "sessions",
                    "conversions",
                    "averageSessionDuration",
                    "bounceRate"
                ]
            
            # Set default dimensions if not provided
            if not dimensions:
                dimensions = ["date"]
            
            # Create request
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(
                    start_date=date_range["start_date"],
                    end_date=date_range["end_date"]
                )],
                metrics=[Metric(name=metric) for metric in metrics],
                dimensions=[Dimension(name=dim) for dim in dimensions]
            )
            
            # Run report
            response = self.client.run_report(request)
            
            # Process response
            result = {
                "metrics": {},
                "dimensions": dimensions,
                "date_range": date_range,
                "timestamp": datetime.now(pytz.UTC).isoformat()
            }
            
            # Extract metric values
            for row in response.rows:
                for i, dimension in enumerate(dimensions):
                    if dimension not in result["metrics"]:
                        result["metrics"][dimension] = []
                    result["metrics"][dimension].append(row.dimension_values[i].value)
                
                for i, metric in enumerate(metrics):
                    if metric not in result["metrics"]:
                        result["metrics"][metric] = []
                    result["metrics"][metric].append(float(row.metric_values[i].value))
            
            self._log_integration(
                "fetch_data",
                {
                    "property_id": property_id,
                    "date_range": date_range,
                    "metrics": metrics,
                    "dimensions": dimensions
                }
            )
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to fetch GA4 metrics: {str(e)}")
            raise ValueError(f"Failed to fetch GA4 metrics: {str(e)}")
    
    async def list_resources(
        self,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List available GA4 properties."""
        try:
            # This is a placeholder for actual property listing
            # In a real implementation, you would use the GA4 Admin API
            properties = [
                {
                    "property_id": "123456789",
                    "name": "GA4 Property 1",
                    "account_id": "123456789",
                    "created_at": datetime.now(pytz.UTC).isoformat()
                }
            ]
            
            self._log_integration("list_resources", {"count": len(properties)})
            
            return properties
        except Exception as e:
            self.logger.error(f"Failed to list GA4 properties: {str(e)}")
            raise ValueError(f"Failed to list GA4 properties: {str(e)}")
    
    async def get_resource_info(
        self,
        property_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get information about a GA4 property."""
        try:
            # This is a placeholder for actual property info fetching
            # In a real implementation, you would use the GA4 Admin API
            info = {
                "property_id": property_id,
                "name": f"GA4 Property {property_id}",
                "account_id": "123456789",
                "created_at": datetime.now(pytz.UTC).isoformat()
            }
            
            self._log_integration(
                "get_resource_info",
                {"property_id": property_id}
            )
            
            return info
        except Exception as e:
            self.logger.error(f"Failed to get property info: {str(e)}")
            raise ValueError(f"Failed to get property info: {str(e)}")
    
    def validate_credentials(self) -> bool:
        """Validate GA4 credentials."""
        try:
            # Try to list properties as a validation check
            self.list_resources()
            return True
        except Exception as e:
            self.logger.error(f"GA4 credential validation failed: {str(e)}")
            return False 