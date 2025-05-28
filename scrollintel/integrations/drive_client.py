"""
ScrollIntel v2: The Flame Interpreter
Google Drive integration client
"""

from typing import Dict, Any, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import pickle
import io
from datetime import datetime
import pytz

from .cloud_storage_client import CloudStorageClient

class DriveClient(CloudStorageClient):
    """Google Drive integration client."""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    TOKEN_PATH = 'credentials/drive_token.pickle'
    CREDENTIALS_PATH = 'credentials/drive_credentials.json'
    
    def __init__(self, credentials: Dict[str, Any]):
        """Initialize Google Drive client with OAuth2 credentials."""
        super().__init__(credentials)
        self.credentials = self._get_credentials()
        self.service = build('drive', 'v3', credentials=self.credentials)
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
                        f"Google Drive credentials file not found at {self.CREDENTIALS_PATH}. "
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
    
    async def _download_file(self, file_id: str) -> bytes:
        """Download file content from Google Drive."""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            
            while not done:
                status, done = downloader.next_chunk()
            
            return file.getvalue()
        except Exception as e:
            self.logger.error(f"Failed to download file: {str(e)}")
            raise ValueError(f"Failed to download file: {str(e)}")
    
    async def _list_files(self, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in Google Drive folder."""
        try:
            # Build query
            query = "trashed = false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            # Add mime type filters
            mime_types = " or ".join([f"mimeType='{mime}'" for mime in self.SUPPORTED_MIMETYPES])
            query += f" and ({mime_types})"
            
            # List files
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields="files(id, name, mimeType, size, createdTime, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            
            # Format file metadata
            return [{
                "id": file["id"],
                "name": file["name"],
                "mime_type": file["mimeType"],
                "size": int(file.get("size", 0)),
                "created": file.get("createdTime", datetime.now(pytz.UTC).isoformat()),
                "modified": file.get("modifiedTime", datetime.now(pytz.UTC).isoformat())
            } for file in files]
        except Exception as e:
            self.logger.error(f"Failed to list files: {str(e)}")
            raise ValueError(f"Failed to list files: {str(e)}")
    
    async def _get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get file metadata from Google Drive."""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, createdTime, modifiedTime"
            ).execute()
            
            return {
                "id": file["id"],
                "name": file["name"],
                "mime_type": file["mimeType"],
                "size": int(file.get("size", 0)),
                "created": file.get("createdTime", datetime.now(pytz.UTC).isoformat()),
                "modified": file.get("modifiedTime", datetime.now(pytz.UTC).isoformat())
            }
        except Exception as e:
            self.logger.error(f"Failed to get file metadata: {str(e)}")
            raise ValueError(f"Failed to get file metadata: {str(e)}")
    
    def validate_credentials(self) -> bool:
        """Validate Google Drive credentials."""
        try:
            # Try to list files as a validation check
            self._list_files()
            return True
        except Exception as e:
            self.logger.error(f"Google Drive credential validation failed: {str(e)}")
            return False 