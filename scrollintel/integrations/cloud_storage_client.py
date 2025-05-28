"""
ScrollIntel v2: The Flame Interpreter
Cloud Storage integration base client
"""

from typing import Dict, Any, List, Optional, Union
import pandas as pd
from datetime import datetime
import pytz
import os
import json
import io
import mimetypes

from .base import BaseIntegration

class CloudStorageClient(BaseIntegration):
    """Base class for cloud storage integrations (Google Drive, OneDrive)."""
    
    SUPPORTED_MIMETYPES = [
        'text/csv',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'application/json'
    ]
    
    def __init__(self, credentials: Dict[str, Any]):
        """Initialize cloud storage client with credentials."""
        super().__init__(credentials)
        self.scroll_folder = "/ScrollIntel"
        self._log_integration("initialize", {"status": "success"})
    
    async def fetch_data(
        self,
        file_id: str,
        file_type: Optional[str] = None,
        **kwargs
    ) -> Union[pd.DataFrame, Dict[str, Any]]:
        """Read file from cloud storage."""
        try:
            # Download file content
            content = await self._download_file(file_id)
            
            # Determine file type if not provided
            if not file_type:
                file_type = self._get_file_type(file_id)
            
            # Read file based on type
            if file_type == "csv":
                data = pd.read_csv(io.BytesIO(content))
            elif file_type in ["xlsx", "xls"]:
                data = pd.read_excel(io.BytesIO(content))
            elif file_type == "json":
                data = json.loads(content)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            self._log_integration(
                "fetch_data",
                {
                    "file_id": file_id,
                    "file_type": file_type,
                    "data_type": type(data).__name__
                }
            )
            
            return data
        except Exception as e:
            self.logger.error(f"Failed to read file: {str(e)}")
            raise ValueError(f"Failed to read file: {str(e)}")
    
    async def list_resources(
        self,
        folder_id: Optional[str] = None,
        file_types: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List files in cloud storage folder."""
        try:
            if not file_types:
                file_types = ["csv", "xlsx", "xls", "json"]
            
            # List files in folder
            files = await self._list_files(folder_id)
            
            # Filter by file type
            result = []
            for file in files:
                file_type = self._get_file_type(file["id"])
                if file_type in file_types:
                    result.append({
                        "id": file["id"],
                        "name": file["name"],
                        "type": file_type,
                        "size": file.get("size", 0),
                        "modified": file.get("modified", datetime.now(pytz.UTC).isoformat()),
                        "mime_type": file.get("mime_type", "")
                    })
            
            self._log_integration(
                "list_resources",
                {
                    "folder_id": folder_id,
                    "file_types": file_types,
                    "count": len(result)
                }
            )
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to list files: {str(e)}")
            raise ValueError(f"Failed to list files: {str(e)}")
    
    async def get_resource_info(
        self,
        file_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get information about a file."""
        try:
            # Get file metadata
            metadata = await self._get_file_metadata(file_id)
            
            info = {
                "id": metadata["id"],
                "name": metadata["name"],
                "type": self._get_file_type(file_id),
                "size": metadata.get("size", 0),
                "created": metadata.get("created", datetime.now(pytz.UTC).isoformat()),
                "modified": metadata.get("modified", datetime.now(pytz.UTC).isoformat()),
                "mime_type": metadata.get("mime_type", "")
            }
            
            self._log_integration(
                "get_resource_info",
                {"file_id": file_id}
            )
            
            return info
        except Exception as e:
            self.logger.error(f"Failed to get file info: {str(e)}")
            raise ValueError(f"Failed to get file info: {str(e)}")
    
    async def _download_file(self, file_id: str) -> bytes:
        """Download file content. Must be implemented by subclasses."""
        raise NotImplementedError
    
    async def _list_files(self, folder_id: Optional[str]) -> List[Dict[str, Any]]:
        """List files in folder. Must be implemented by subclasses."""
        raise NotImplementedError
    
    async def _get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get file metadata. Must be implemented by subclasses."""
        raise NotImplementedError
    
    def _get_file_type(self, file_id: str) -> str:
        """Get file type from file ID or metadata."""
        try:
            metadata = self._get_file_metadata(file_id)
            mime_type = metadata.get("mime_type", "")
            
            if mime_type == "text/csv":
                return "csv"
            elif mime_type in [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel"
            ]:
                return "xlsx"
            elif mime_type == "application/json":
                return "json"
            else:
                # Try to infer from file extension
                ext = os.path.splitext(metadata["name"])[1].lower()
                if ext == ".csv":
                    return "csv"
                elif ext in [".xlsx", ".xls"]:
                    return "xlsx"
                elif ext == ".json":
                    return "json"
                else:
                    raise ValueError(f"Unsupported file type: {mime_type}")
        except Exception as e:
            self.logger.error(f"Failed to get file type: {str(e)}")
            raise ValueError(f"Failed to get file type: {str(e)}") 