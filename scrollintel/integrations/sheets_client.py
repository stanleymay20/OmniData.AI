"""
ScrollIntel v2: The Flame Interpreter
Google Sheets integration client
"""

from typing import Dict, Any, List, Optional, Union
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pandas as pd
import os
import json
import pickle
from datetime import datetime
import pytz
import re

from .base import BaseIntegration

class SheetsClient(BaseIntegration):
    """Google Sheets integration client."""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    TOKEN_PATH = 'credentials/sheets_token.pickle'
    CREDENTIALS_PATH = 'credentials/sheets_credentials.json'
    
    def __init__(self, credentials: Dict[str, Any]):
        """Initialize Google Sheets client with OAuth2 credentials."""
        super().__init__(credentials)
        self.credentials = self._get_credentials()
        self.service = build('sheets', 'v4', credentials=self.credentials)
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
                        f"Google Sheets credentials file not found at {self.CREDENTIALS_PATH}. "
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
    
    def _extract_sheet_id(self, url: str) -> str:
        """Extract sheet ID from Google Sheets URL."""
        # Match patterns like:
        # https://docs.google.com/spreadsheets/d/SHEET_ID/edit
        # https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=0
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if not match:
            raise ValueError("Invalid Google Sheets URL")
        return match.group(1)
    
    async def fetch_data(
        self,
        sheet_url: str,
        sheet_name: Optional[str] = None,
        range_name: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """Fetch data from Google Sheet."""
        try:
            # Extract sheet ID from URL
            sheet_id = self._extract_sheet_id(sheet_url)
            
            # Get sheet metadata
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            # If sheet name not provided, use first sheet
            if not sheet_name:
                sheet_name = sheet_metadata['sheets'][0]['properties']['title']
            
            # If range not provided, use entire sheet
            if not range_name:
                range_name = f"{sheet_name}!A1:ZZ"
            
            # Fetch data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            # Convert to DataFrame
            values = result.get('values', [])
            if not values:
                raise ValueError("No data found in sheet")
            
            # Use first row as headers
            headers = values[0]
            data = values[1:]
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=headers)
            
            self._log_integration(
                "fetch_data",
                {
                    "sheet_id": sheet_id,
                    "sheet_name": sheet_name,
                    "range": range_name,
                    "rows": len(df)
                }
            )
            
            return df
        except Exception as e:
            self.logger.error(f"Failed to fetch sheet data: {str(e)}")
            raise ValueError(f"Failed to fetch sheet data: {str(e)}")
    
    async def list_resources(
        self,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List available Google Sheets."""
        try:
            # Get list of spreadsheets
            results = self.service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                spaces='drive',
                fields="files(id, name, createdTime, modifiedTime)"
            ).execute()
            
            sheets = results.get('files', [])
            
            self._log_integration(
                "list_resources",
                {"count": len(sheets)}
            )
            
            return sheets
        except Exception as e:
            self.logger.error(f"Failed to list sheets: {str(e)}")
            raise ValueError(f"Failed to list sheets: {str(e)}")
    
    async def get_resource_info(
        self,
        sheet_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get information about a Google Sheet."""
        try:
            # Get sheet metadata
            metadata = self.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            info = {
                "id": metadata['spreadsheetId'],
                "title": metadata['properties']['title'],
                "created": metadata['properties']['createdTime'],
                "modified": metadata['properties']['updatedTime'],
                "sheets": [
                    {
                        "id": sheet['properties']['sheetId'],
                        "title": sheet['properties']['title'],
                        "index": sheet['properties']['index']
                    }
                    for sheet in metadata['sheets']
                ]
            }
            
            self._log_integration(
                "get_resource_info",
                {"sheet_id": sheet_id}
            )
            
            return info
        except Exception as e:
            self.logger.error(f"Failed to get sheet info: {str(e)}")
            raise ValueError(f"Failed to get sheet info: {str(e)}")
    
    def validate_credentials(self) -> bool:
        """Validate Google Sheets credentials."""
        try:
            # Try to list sheets as a validation check
            self.list_resources()
            return True
        except Exception as e:
            self.logger.error(f"Google Sheets credential validation failed: {str(e)}")
            return False 