"""
ScrollIntel Cloud Sync Service
Handles scheduled synchronization of cloud storage sources
"""

import os
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import dropbox
from dropbox.exceptions import ApiError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

from ..utils.config import get_settings
from ..interpreters.flame import FlameInterpreter
from ..memory.scroll_memory import ScrollMemory

logger = logging.getLogger(__name__)

class CloudSyncService:
    def __init__(self):
        self.settings = get_settings()
        self.scheduler = BackgroundScheduler()
        self.sync_status: Dict[str, Dict] = {
            'dropbox': {'last_sync': None, 'status': 'idle'},
            'gdrive': {'last_sync': None, 'status': 'idle'},
            'onedrive': {'last_sync': None, 'status': 'idle'}
        }
        self.flame = FlameInterpreter()
        self.memory = ScrollMemory()
        
        # Initialize cloud clients
        self._init_dropbox()
        self._init_gdrive()
        self._init_onedrive()
        
        # Start scheduler
        self.scheduler.start()
        self.scheduler.add_job(
            self.sync_all_sources,
            trigger=IntervalTrigger(seconds=self.settings.CLOUD_SYNC_INTERVAL),
            id='cloud_sync',
            replace_existing=True
        )

    def _init_dropbox(self):
        """Initialize Dropbox client"""
        try:
            self.dropbox_client = dropbox.Dropbox(
                oauth2_refresh_token=self.settings.DROPBOX_ACCESS_TOKEN,
                app_key=self.settings.DROPBOX_CLIENT_ID,
                app_secret=self.settings.DROPBOX_CLIENT_SECRET
            )
        except Exception as e:
            logger.error(f"Failed to initialize Dropbox client: {e}")
            self.dropbox_client = None

    def _init_gdrive(self):
        """Initialize Google Drive client"""
        try:
            credentials = Credentials.from_authorized_user_info({
                'client_id': self.settings.DRIVE_CLIENT_ID,
                'client_secret': self.settings.DRIVE_CLIENT_SECRET,
                'refresh_token': self.settings.DRIVE_REFRESH_TOKEN
            })
            self.gdrive_client = build('drive', 'v3', credentials=credentials)
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive client: {e}")
            self.gdrive_client = None

    def _init_onedrive(self):
        """Initialize OneDrive client"""
        # TODO: Implement OneDrive client initialization
        self.onedrive_client = None

    async def sync_all_sources(self):
        """Sync all cloud sources"""
        await self.sync_dropbox()
        await self.sync_gdrive()
        await self.sync_onedrive()

    async def sync_dropbox(self):
        """Sync files from Dropbox"""
        if not self.dropbox_client:
            logger.error("Dropbox client not initialized")
            return

        try:
            self.sync_status['dropbox']['status'] = 'syncing'
            
            # List files in the auto directory
            result = self.dropbox_client.files_list_folder(
                self.settings.CLOUD_SYNC_PATH
            )
            
            for entry in result.entries:
                if not self._is_valid_file(entry.name):
                    continue
                    
                # Download and process file
                _, response = self.dropbox_client.files_download(entry.path_display)
                file_content = response.content
                
                # Process file with Flame interpreter
                interpretation = await self.flame.interpret_file(
                    file_content,
                    filename=entry.name
                )
                
                # Store in ScrollMemory
                await self.memory.store_interpretation(interpretation)
                
            self.sync_status['dropbox']['last_sync'] = datetime.now()
            self.sync_status['dropbox']['status'] = 'success'
            
        except ApiError as e:
            logger.error(f"Dropbox API error: {e}")
            self.sync_status['dropbox']['status'] = 'error'
        except Exception as e:
            logger.error(f"Error syncing Dropbox: {e}")
            self.sync_status['dropbox']['status'] = 'error'

    async def sync_gdrive(self):
        """Sync files from Google Drive"""
        if not self.gdrive_client:
            logger.error("Google Drive client not initialized")
            return

        try:
            self.sync_status['gdrive']['status'] = 'syncing'
            
            # List files in the auto directory
            results = self.gdrive_client.files().list(
                q=f"'{self.settings.CLOUD_SYNC_PATH}' in parents",
                fields="files(id, name)"
            ).execute()
            
            for file in results.get('files', []):
                if not self._is_valid_file(file['name']):
                    continue
                    
                # Download file
                request = self.gdrive_client.files().get_media(fileId=file['id'])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                
                # Process file with Flame interpreter
                interpretation = await self.flame.interpret_file(
                    fh.getvalue(),
                    filename=file['name']
                )
                
                # Store in ScrollMemory
                await self.memory.store_interpretation(interpretation)
                
            self.sync_status['gdrive']['last_sync'] = datetime.now()
            self.sync_status['gdrive']['status'] = 'success'
            
        except Exception as e:
            logger.error(f"Error syncing Google Drive: {e}")
            self.sync_status['gdrive']['status'] = 'error'

    async def sync_onedrive(self):
        """Sync files from OneDrive"""
        # TODO: Implement OneDrive sync
        pass

    def _is_valid_file(self, filename: str) -> bool:
        """Check if file is valid for processing"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in ['.csv', '.xlsx']

    def get_sync_status(self) -> Dict[str, Dict]:
        """Get current sync status for all sources"""
        return self.sync_status

    def stop(self):
        """Stop the sync scheduler"""
        self.scheduler.shutdown()

# Create global instance
cloud_sync = CloudSyncService() 