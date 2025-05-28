"""
ScrollIntel v2: The Flame Interpreter
Airtable integration client
"""

from typing import Dict, Any, List, Optional, Union
import pandas as pd
from datetime import datetime
import pytz
import os
import json
import requests

from .base import BaseIntegration

class AirtableClient(BaseIntegration):
    """Airtable integration client."""
    
    BASE_URL = "https://api.airtable.com/v0"
    
    def __init__(self, credentials: Dict[str, Any]):
        """Initialize Airtable client with credentials."""
        super().__init__(credentials)
        self.api_key = credentials["api_key"]
        self.base_id = credentials["base_id"]
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self._log_integration("initialize", {"status": "success"})
    
    async def fetch_data(
        self,
        table_id: str,
        fields: Optional[List[str]] = None,
        filter_by_formula: Optional[str] = None,
        max_records: Optional[int] = 100,
        **kwargs
    ) -> pd.DataFrame:
        """Fetch data from Airtable table."""
        try:
            # Build URL
            url = f"{self.BASE_URL}/{self.base_id}/{table_id}"
            
            # Build params
            params = {
                "maxRecords": max_records
            }
            if filter_by_formula:
                params["filterByFormula"] = filter_by_formula
            
            # Make request
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            records = data.get("records", [])
            
            # Convert to DataFrame
            rows = []
            for record in records:
                row = record["fields"]
                row["id"] = record["id"]
                row["createdTime"] = record["createdTime"]
                rows.append(row)
            
            df = pd.DataFrame(rows)
            
            # Filter fields if specified
            if fields:
                df = df[fields]
            
            self._log_integration(
                "fetch_data",
                {
                    "table_id": table_id,
                    "fields": fields,
                    "filter_by_formula": filter_by_formula,
                    "max_records": max_records,
                    "rows": len(df)
                }
            )
            
            return df
        except Exception as e:
            self.logger.error(f"Failed to fetch Airtable data: {str(e)}")
            raise ValueError(f"Failed to fetch Airtable data: {str(e)}")
    
    async def list_resources(
        self,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List available Airtable tables."""
        try:
            # Get base schema
            url = f"{self.BASE_URL}/meta/bases/{self.base_id}/tables"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            tables = data.get("tables", [])
            
            # Format table info
            result = []
            for table in tables:
                result.append({
                    "id": table["id"],
                    "name": table["name"],
                    "primary_field_id": table["primaryFieldId"],
                    "fields": [
                        {
                            "id": field["id"],
                            "name": field["name"],
                            "type": field["type"]
                        }
                        for field in table["fields"]
                    ]
                })
            
            self._log_integration(
                "list_resources",
                {"count": len(result)}
            )
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to list Airtable tables: {str(e)}")
            raise ValueError(f"Failed to list Airtable tables: {str(e)}")
    
    async def get_resource_info(
        self,
        table_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get information about an Airtable table."""
        try:
            # Get table schema
            url = f"{self.BASE_URL}/meta/bases/{self.base_id}/tables/{table_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse response
            table = response.json()
            
            info = {
                "id": table["id"],
                "name": table["name"],
                "primary_field_id": table["primaryFieldId"],
                "fields": [
                    {
                        "id": field["id"],
                        "name": field["name"],
                        "type": field["type"],
                        "description": field.get("description"),
                        "options": field.get("options")
                    }
                    for field in table["fields"]
                ]
            }
            
            self._log_integration(
                "get_resource_info",
                {"table_id": table_id}
            )
            
            return info
        except Exception as e:
            self.logger.error(f"Failed to get table info: {str(e)}")
            raise ValueError(f"Failed to get table info: {str(e)}")
    
    def validate_credentials(self) -> bool:
        """Validate Airtable credentials."""
        try:
            # Try to list tables as a validation check
            self.list_resources()
            return True
        except Exception as e:
            self.logger.error(f"Airtable credential validation failed: {str(e)}")
            return False 