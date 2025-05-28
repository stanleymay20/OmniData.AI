"""
ScrollIntel v2: The Flame Interpreter
Salesforce integration client
"""

from typing import Dict, Any, List, Optional, Union
import pandas as pd
from datetime import datetime
import pytz
import os
import json
from simple_salesforce import Salesforce

from .base import BaseIntegration

class SalesforceClient(BaseIntegration):
    """Salesforce integration client."""
    
    SUPPORTED_OBJECTS = [
        "Account",
        "Contact",
        "Lead",
        "Opportunity",
        "Case",
        "Campaign",
        "Product2",
        "Pricebook2",
        "Order",
        "Asset"
    ]
    
    def __init__(self, credentials: Dict[str, Any]):
        """Initialize Salesforce client with credentials."""
        super().__init__(credentials)
        self.client = Salesforce(
            username=credentials["username"],
            password=credentials["password"],
            security_token=credentials["security_token"],
            domain=credentials.get("domain", "login")
        )
        self._log_integration("initialize", {"status": "success"})
    
    async def fetch_data(
        self,
        object_name: str,
        fields: Optional[List[str]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 1000,
        **kwargs
    ) -> pd.DataFrame:
        """Fetch data from Salesforce object."""
        try:
            # Validate object name
            if object_name not in self.SUPPORTED_OBJECTS:
                raise ValueError(f"Unsupported object: {object_name}")
            
            # Get all fields if not specified
            if not fields:
                fields = self._get_object_fields(object_name)
            
            # Build SOQL query
            query = f"SELECT {','.join(fields)} FROM {object_name}"
            
            # Add conditions
            if conditions:
                where_clauses = []
                for field, value in conditions.items():
                    if isinstance(value, str):
                        where_clauses.append(f"{field} = '{value}'")
                    else:
                        where_clauses.append(f"{field} = {value}")
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Add limit
            query += f" LIMIT {limit}"
            
            # Execute query
            result = self.client.query(query)
            
            # Convert to DataFrame
            records = result["records"]
            df = pd.DataFrame(records)
            
            # Remove Salesforce metadata columns
            df = df.drop(columns=["attributes"], errors="ignore")
            
            self._log_integration(
                "fetch_data",
                {
                    "object": object_name,
                    "fields": fields,
                    "conditions": conditions,
                    "limit": limit,
                    "rows": len(df)
                }
            )
            
            return df
        except Exception as e:
            self.logger.error(f"Failed to fetch Salesforce data: {str(e)}")
            raise ValueError(f"Failed to fetch Salesforce data: {str(e)}")
    
    async def list_resources(
        self,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List available Salesforce objects."""
        try:
            # Get object descriptions
            objects = []
            for obj_name in self.SUPPORTED_OBJECTS:
                try:
                    desc = self.client.__getattr__(obj_name).describe()
                    objects.append({
                        "name": obj_name,
                        "label": desc["label"],
                        "label_plural": desc["labelPlural"],
                        "fields": len(desc["fields"]),
                        "createable": desc["createable"],
                        "updateable": desc["updateable"],
                        "deletable": desc["deletable"]
                    })
                except Exception:
                    continue
            
            self._log_integration(
                "list_resources",
                {"count": len(objects)}
            )
            
            return objects
        except Exception as e:
            self.logger.error(f"Failed to list Salesforce objects: {str(e)}")
            raise ValueError(f"Failed to list Salesforce objects: {str(e)}")
    
    async def get_resource_info(
        self,
        object_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get information about a Salesforce object."""
        try:
            # Validate object name
            if object_name not in self.SUPPORTED_OBJECTS:
                raise ValueError(f"Unsupported object: {object_name}")
            
            # Get object description
            desc = self.client.__getattr__(object_name).describe()
            
            # Get field information
            fields = []
            for field in desc["fields"]:
                fields.append({
                    "name": field["name"],
                    "label": field["label"],
                    "type": field["type"],
                    "length": field.get("length"),
                    "precision": field.get("precision"),
                    "scale": field.get("scale"),
                    "picklist_values": [
                        {
                            "label": value["label"],
                            "value": value["value"]
                        }
                        for value in field.get("picklistValues", [])
                    ] if field["type"] == "picklist" else None
                })
            
            info = {
                "name": object_name,
                "label": desc["label"],
                "label_plural": desc["labelPlural"],
                "fields": fields,
                "createable": desc["createable"],
                "updateable": desc["updateable"],
                "deletable": desc["deletable"],
                "queryable": desc["queryable"],
                "retrieveable": desc["retrieveable"],
                "searchable": desc["searchable"]
            }
            
            self._log_integration(
                "get_resource_info",
                {"object": object_name}
            )
            
            return info
        except Exception as e:
            self.logger.error(f"Failed to get object info: {str(e)}")
            raise ValueError(f"Failed to get object info: {str(e)}")
    
    def _get_object_fields(self, object_name: str) -> List[str]:
        """Get all fields for a Salesforce object."""
        try:
            desc = self.client.__getattr__(object_name).describe()
            return [field["name"] for field in desc["fields"]]
        except Exception as e:
            self.logger.error(f"Failed to get object fields: {str(e)}")
            raise ValueError(f"Failed to get object fields: {str(e)}")
    
    def validate_credentials(self) -> bool:
        """Validate Salesforce credentials."""
        try:
            # Try to list objects as a validation check
            self.list_resources()
            return True
        except Exception as e:
            self.logger.error(f"Salesforce credential validation failed: {str(e)}")
            return False 