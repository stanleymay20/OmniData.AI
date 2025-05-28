"""
ScrollIntel v2: The Flame Interpreter
OneDrive integration client
"""

from typing import Dict, Any, List, Optional
import msal
import requests
import json
from datetime import datetime, timedelta
import pytz
import os

from .cloud_storage_client import CloudStorageClient

class OneDriveClient(CloudStorageClient):
    """OneDrive integration client."""
    
    TOKEN_PATH = 'credentials/onedrive_token.json'
    CREDENTIALS_PATH = 'credentials/onedrive_credentials.json'
    
    def __init__(self, credentials: Dict[str, Any]):
        """Initialize OneDrive client with OAuth2 credentials."""
        super().__init__(credentials)
        self.credentials = self._get_credentials()
        self.access_token = self.credentials["access_token"]
        self._log_integration("initialize", {"status": "success"})
    
    def _get_credentials(self) -> Dict[str, Any]:
        """Get or refresh OAuth2 credentials."""
        # Create credentials directory if it doesn't exist
        os.makedirs('credentials', exist_ok=True)
        
        # Load existing token
        if os.path.exists(self.TOKEN_PATH):
            with open(self.TOKEN_PATH, 'r') as token:
                creds = json.load(token)
            
            # Check if token needs refresh
            if datetime.fromisoformat(creds["expires_at"]) > datetime.now(pytz.UTC):
                return creds
        
        # Initialize MSAL app
        app = msal.ConfidentialClientApplication(
            client_id=self.credentials["client_id"],
            client_credential=self.credentials["client_secret"],
            authority=f"https://login.microsoftonline.com/{self.credentials['tenant_id']}"
        )
        
        # Get token
        result = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        
        if "access_token" not in result:
            raise ValueError(f"Failed to get access token: {result.get('error_description', 'Unknown error')}")
        
        # Save token
        creds = {
            "access_token": result["access_token"],
            "expires_at": (datetime.now(pytz.UTC) + timedelta(seconds=result["expires_in"])).isoformat()
        }
        
        with open(self.TOKEN_PATH, 'w') as token:
            json.dump(creds, token)
        
        return creds
    
    async def _download_file(self, file_id: str) -> bytes:
        """Download file content from OneDrive."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content",
                headers=headers
            )
            
            if response.status_code != 200:
                raise ValueError(f"Failed to download file: {response.text}")
            
            return response.content
        except Exception as e:
            self.logger.error(f"Failed to download file: {str(e)}")
            raise ValueError(f"Failed to download file: {str(e)}")
    
    async def _list_files(self, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in OneDrive folder."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Build URL
            if folder_id:
                url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
            else:
                url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
            
            # Add filter for supported file types
            url += "?$filter=" + " or ".join([
                f"file/mimeType eq '{mime}'" for mime in self.SUPPORTED_MIMETYPES
            ])
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                raise ValueError(f"Failed to list files: {response.text}")
            
            data = response.json()
            files = data.get("value", [])
            
            # Format file metadata
            return [{
                "id": file["id"],
                "name": file["name"],
                "mime_type": file.get("file", {}).get("mimeType", ""),
                "size": int(file.get("size", 0)),
                "created": file.get("createdDateTime", datetime.now(pytz.UTC).isoformat()),
                "modified": file.get("lastModifiedDateTime", datetime.now(pytz.UTC).isoformat())
            } for file in files]
        except Exception as e:
            self.logger.error(f"Failed to list files: {str(e)}")
            raise ValueError(f"Failed to list files: {str(e)}")
    
    async def _get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get file metadata from OneDrive."""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                raise ValueError(f"Failed to get file metadata: {response.text}")
            
            file = response.json()
            
            return {
                "id": file["id"],
                "name": file["name"],
                "mime_type": file.get("file", {}).get("mimeType", ""),
                "size": int(file.get("size", 0)),
                "created": file.get("createdDateTime", datetime.now(pytz.UTC).isoformat()),
                "modified": file.get("lastModifiedDateTime", datetime.now(pytz.UTC).isoformat())
            }
        except Exception as e:
            self.logger.error(f"Failed to get file metadata: {str(e)}")
            raise ValueError(f"Failed to get file metadata: {str(e)}")
    
    def validate_credentials(self) -> bool:
        """Validate OneDrive credentials."""
        try:
            # Try to list files as a validation check
            self._list_files()
            return True
        except Exception as e:
            self.logger.error(f"OneDrive credential validation failed: {str(e)}")
            return False 