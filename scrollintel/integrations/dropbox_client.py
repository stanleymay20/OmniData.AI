"""
ScrollIntel v2: The Flame Interpreter
Dropbox integration client
"""

from typing import Dict, Any, List, Optional, Union
import dropbox
from dropbox.files import FileMetadata, FolderMetadata
import pandas as pd
import json
import io
from datetime import datetime
import pytz
import os

from .base import BaseIntegration

class DropboxClient(BaseIntegration):
    """Dropbox integration client."""
    
    def __init__(self, credentials: Dict[str, Any]):
        """Initialize Dropbox client with access token."""
        super().__init__(credentials)
        self.client = dropbox.Dropbox(credentials["access_token"])
        self.scroll_folder = "/ScrollIntel"
        self._log_integration("initialize", {"status": "success"})
    
    async def fetch_data(
        self,
        path: str,
        file_type: Optional[str] = None,
        **kwargs
    ) -> Union[pd.DataFrame, Dict[str, Any]]:
        """Read file from Dropbox."""
        try:
            # Download file
            _, response = self.client.files_download(path)
            
            # Determine file type if not provided
            if not file_type:
                file_type = os.path.splitext(path)[1].lower()
            
            # Read file based on type
            if file_type == ".csv":
                data = pd.read_csv(io.BytesIO(response.content))
            elif file_type == ".xlsx":
                data = pd.read_excel(io.BytesIO(response.content))
            elif file_type == ".json":
                data = json.loads(response.content)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            self._log_integration(
                "fetch_data",
                {
                    "path": path,
                    "file_type": file_type,
                    "data_type": type(data).__name__
                }
            )
            
            return data
        except Exception as e:
            self.logger.error(f"Failed to read Dropbox file: {str(e)}")
            raise ValueError(f"Failed to read Dropbox file: {str(e)}")
    
    async def list_resources(
        self,
        path: str = "/ScrollIntel",
        file_types: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List files in Dropbox folder."""
        try:
            if not file_types:
                file_types = [".csv", ".xlsx", ".json"]
            
            result = []
            
            # List files in folder
            response = self.client.files_list_folder(path)
            
            for entry in response.entries:
                if isinstance(entry, FileMetadata):
                    # Check file extension
                    if any(entry.name.endswith(ext) for ext in file_types):
                        result.append({
                            "name": entry.name,
                            "path": entry.path_display,
                            "size": entry.size,
                            "modified": entry.server_modified.isoformat(),
                            "type": "file"
                        })
                elif isinstance(entry, FolderMetadata):
                    result.append({
                        "name": entry.name,
                        "path": entry.path_display,
                        "type": "folder"
                    })
            
            self._log_integration(
                "list_resources",
                {
                    "path": path,
                    "file_types": file_types,
                    "count": len(result)
                }
            )
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to list Dropbox files: {str(e)}")
            raise ValueError(f"Failed to list Dropbox files: {str(e)}")
    
    async def get_resource_info(
        self,
        path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get information about a Dropbox file or folder."""
        try:
            metadata = self.client.files_get_metadata(path)
            
            info = {
                "name": metadata.name,
                "path": metadata.path_display,
                "type": "folder" if isinstance(metadata, FolderMetadata) else "file",
                "created": metadata.server_created.isoformat(),
                "modified": metadata.server_modified.isoformat()
            }
            
            if isinstance(metadata, FileMetadata):
                info["size"] = metadata.size
            
            self._log_integration(
                "get_resource_info",
                {"path": path}
            )
            
            return info
        except Exception as e:
            self.logger.error(f"Failed to get file info: {str(e)}")
            raise ValueError(f"Failed to get file info: {str(e)}")
    
    async def upload_file(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        path: str,
        file_type: str
    ) -> Dict[str, Any]:
        """Upload file to Dropbox."""
        try:
            # Convert data to bytes
            if isinstance(data, pd.DataFrame):
                if file_type == ".csv":
                    content = data.to_csv(index=False).encode()
                elif file_type == ".xlsx":
                    buffer = io.BytesIO()
                    data.to_excel(buffer, index=False)
                    content = buffer.getvalue()
                else:
                    raise ValueError(f"Unsupported file type for DataFrame: {file_type}")
            elif isinstance(data, dict):
                if file_type == ".json":
                    content = json.dumps(data).encode()
                else:
                    raise ValueError(f"Unsupported file type for dict: {file_type}")
            else:
                raise ValueError("Unsupported data type")
            
            # Upload file
            response = self.client.files_upload(
                content,
                path,
                mode=dropbox.files.WriteMode.overwrite
            )
            
            result = {
                "name": response.name,
                "path": response.path_display,
                "size": response.size,
                "modified": response.server_modified.isoformat()
            }
            
            self._log_integration(
                "upload_file",
                {
                    "path": path,
                    "file_type": file_type,
                    "data_type": type(data).__name__
                }
            )
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to upload file to Dropbox: {str(e)}")
            raise ValueError(f"Failed to upload file to Dropbox: {str(e)}")
    
    def validate_credentials(self) -> bool:
        """Validate Dropbox credentials."""
        try:
            # Try to get account info as a validation check
            self.client.users_get_current_account()
            return True
        except Exception as e:
            self.logger.error(f"Dropbox credential validation failed: {str(e)}")
            return False 