"""
ScrollIntel v2: The Flame Interpreter
Notion integration client
"""

from typing import Dict, Any, List, Optional, Union
import pandas as pd
from datetime import datetime
import pytz
import os
import json
import requests

from .base import BaseIntegration

class NotionClient(BaseIntegration):
    """Notion integration client."""
    
    BASE_URL = "https://api.notion.com/v1"
    
    def __init__(self, credentials: Dict[str, Any]):
        """Initialize Notion client with credentials."""
        super().__init__(credentials)
        self.api_key = credentials["api_key"]
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self._log_integration("initialize", {"status": "success"})
    
    async def fetch_data(
        self,
        database_id: str,
        filter_by: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
        page_size: Optional[int] = 100,
        **kwargs
    ) -> pd.DataFrame:
        """Fetch data from Notion database."""
        try:
            # Build URL
            url = f"{self.BASE_URL}/databases/{database_id}/query"
            
            # Build request body
            body = {
                "page_size": page_size
            }
            if filter_by:
                body["filter"] = filter_by
            if sorts:
                body["sorts"] = sorts
            
            # Make request
            response = requests.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            results = data.get("results", [])
            
            # Convert to DataFrame
            rows = []
            for page in results:
                row = {}
                for key, value in page["properties"].items():
                    row[key] = self._parse_property_value(value)
                row["id"] = page["id"]
                row["created_time"] = page["created_time"]
                row["last_edited_time"] = page["last_edited_time"]
                rows.append(row)
            
            df = pd.DataFrame(rows)
            
            self._log_integration(
                "fetch_data",
                {
                    "database_id": database_id,
                    "filter_by": filter_by,
                    "sorts": sorts,
                    "page_size": page_size,
                    "rows": len(df)
                }
            )
            
            return df
        except Exception as e:
            self.logger.error(f"Failed to fetch Notion data: {str(e)}")
            raise ValueError(f"Failed to fetch Notion data: {str(e)}")
    
    async def list_resources(
        self,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List available Notion databases."""
        try:
            # Search for databases
            url = f"{self.BASE_URL}/search"
            body = {
                "filter": {
                    "property": "object",
                    "value": "database"
                }
            }
            
            response = requests.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            results = data.get("results", [])
            
            # Format database info
            databases = []
            for db in results:
                databases.append({
                    "id": db["id"],
                    "title": self._get_database_title(db),
                    "url": db["url"],
                    "created_time": db["created_time"],
                    "last_edited_time": db["last_edited_time"]
                })
            
            self._log_integration(
                "list_resources",
                {"count": len(databases)}
            )
            
            return databases
        except Exception as e:
            self.logger.error(f"Failed to list Notion databases: {str(e)}")
            raise ValueError(f"Failed to list Notion databases: {str(e)}")
    
    async def get_resource_info(
        self,
        database_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get information about a Notion database."""
        try:
            # Get database metadata
            url = f"{self.BASE_URL}/databases/{database_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse response
            db = response.json()
            
            info = {
                "id": db["id"],
                "title": self._get_database_title(db),
                "url": db["url"],
                "created_time": db["created_time"],
                "last_edited_time": db["last_edited_time"],
                "properties": [
                    {
                        "id": prop["id"],
                        "name": prop["name"],
                        "type": prop["type"]
                    }
                    for prop in db["properties"].values()
                ]
            }
            
            self._log_integration(
                "get_resource_info",
                {"database_id": database_id}
            )
            
            return info
        except Exception as e:
            self.logger.error(f"Failed to get database info: {str(e)}")
            raise ValueError(f"Failed to get database info: {str(e)}")
    
    def _parse_property_value(self, property_value: Dict[str, Any]) -> Any:
        """Parse Notion property value based on type."""
        prop_type = property_value["type"]
        
        if prop_type == "title":
            return property_value["title"][0]["plain_text"] if property_value["title"] else None
        elif prop_type == "rich_text":
            return property_value["rich_text"][0]["plain_text"] if property_value["rich_text"] else None
        elif prop_type == "number":
            return property_value["number"]
        elif prop_type == "select":
            return property_value["select"]["name"] if property_value["select"] else None
        elif prop_type == "multi_select":
            return [option["name"] for option in property_value["multi_select"]]
        elif prop_type == "date":
            return property_value["date"]["start"] if property_value["date"] else None
        elif prop_type == "people":
            return [person["name"] for person in property_value["people"]]
        elif prop_type == "files":
            return [file["name"] for file in property_value["files"]]
        elif prop_type == "checkbox":
            return property_value["checkbox"]
        elif prop_type == "url":
            return property_value["url"]
        elif prop_type == "email":
            return property_value["email"]
        elif prop_type == "phone_number":
            return property_value["phone_number"]
        else:
            return None
    
    def _get_database_title(self, database: Dict[str, Any]) -> str:
        """Get database title from title property."""
        title_property = database.get("title", [])
        if title_property:
            return title_property[0]["plain_text"]
        return "Untitled"
    
    def validate_credentials(self) -> bool:
        """Validate Notion credentials."""
        try:
            # Try to list databases as a validation check
            self.list_resources()
            return True
        except Exception as e:
            self.logger.error(f"Notion credential validation failed: {str(e)}")
            return False 