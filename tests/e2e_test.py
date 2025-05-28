"""
ScrollIntel v2 End-to-End Test Suite
Tests all major components and integrations
"""

import os
import json
import asyncio
import logging
from datetime import datetime
import pytz
from pathlib import Path
import pandas as pd
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('e2e_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScrollIntelE2ETest:
    def __init__(self):
        """Initialize test suite."""
        load_dotenv()
        self.base_url = "http://localhost:8000"
        self.token = None
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }

    async def run_all_tests(self):
        """Run all end-to-end tests."""
        logger.info("Starting end-to-end tests...")
        
        # Login to get token
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={
                    "username": os.getenv("TEST_USERNAME"),
                    "password": os.getenv("TEST_PASSWORD")
                }
            )
            response.raise_for_status()
            self.token = response.json()["access_token"]
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return
        
        # Run tests
        await self.test_openai_integration()
        await self.test_dropbox_integration()
        await self.test_google_oauth()
        await self.test_scroll_prophet()
        await self.test_pdf_export()
        await self.test_github_push()
        await self.test_cloud_sync()
        await self.test_dashboard()
        
        # Save results
        self.save_results()
        logger.info("End-to-end tests completed")

    async def test_openai_integration(self):
        """Test OpenAI integration"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"message": "Test message"}
            )
            response.raise_for_status()
            self.results["tests"]["openai"] = {
                "status": "success",
                "response": response.json()
            }
        except Exception as e:
            logger.error(f"OpenAI test failed: {e}")
            self.results["tests"]["openai"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_dropbox_integration(self):
        """Test Dropbox integration"""
        try:
            # Test sync status
            response = requests.get(
                f"{self.base_url}/api/sync/status",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            status = response.json()
            
            # Test manual sync
            response = requests.post(
                f"{self.base_url}/api/sync/trigger/dropbox",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            
            self.results["tests"]["dropbox"] = {
                "status": "success",
                "sync_status": status,
                "sync_response": response.json()
            }
        except Exception as e:
            logger.error(f"Dropbox test failed: {e}")
            self.results["tests"]["dropbox"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_google_oauth(self):
        """Test Google OAuth integration"""
        try:
            # Test GA4 auth
            response = requests.get(
                f"{self.base_url}/auth/ga4/login",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            
            # Test Sheets auth
            response = requests.get(
                f"{self.base_url}/auth/sheets/login",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            
            self.results["tests"]["google_oauth"] = {
                "status": "success",
                "ga4_auth": response.json()
            }
        except Exception as e:
            logger.error(f"Google OAuth test failed: {e}")
            self.results["tests"]["google_oauth"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_scroll_prophet(self):
        """Test ScrollProphet AI Assistant"""
        try:
            response = requests.post(
                f"{self.base_url}/api/scroll-chat",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"message": "What's the weather like?"}
            )
            response.raise_for_status()
            self.results["tests"]["scrollprophet"] = {
                "status": "success",
                "response": response.json()
            }
        except Exception as e:
            logger.error(f"ScrollProphet test failed: {e}")
            self.results["tests"]["scrollprophet"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_pdf_export(self):
        """Test PDF report generation"""
        try:
            response = requests.post(
                f"{self.base_url}/api/export/pdf",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"session_id": "test_session"}
            )
            response.raise_for_status()
            self.results["tests"]["pdf_export"] = {
                "status": "success",
                "response": response.json()
            }
        except Exception as e:
            logger.error(f"PDF export test failed: {e}")
            self.results["tests"]["pdf_export"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_github_push(self):
        """Test GitHub repository creation and file push"""
        try:
            response = requests.post(
                f"{self.base_url}/api/export/github",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "session_id": "test_session",
                    "repo_name": "test-repo",
                    "description": "Test repository"
                }
            )
            response.raise_for_status()
            self.results["tests"]["github_push"] = {
                "status": "success",
                "response": response.json()
            }
        except Exception as e:
            logger.error(f"GitHub push test failed: {e}")
            self.results["tests"]["github_push"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_cloud_sync(self):
        """Test cloud sync functionality"""
        try:
            # Test sync status
            response = requests.get(
                f"{self.base_url}/api/sync/status",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            status = response.json()
            
            # Test manual sync
            response = requests.post(
                f"{self.base_url}/api/sync/trigger",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            
            self.results["tests"]["cloud_sync"] = {
                "status": "success",
                "sync_status": status,
                "sync_response": response.json()
            }
        except Exception as e:
            logger.error(f"Cloud sync test failed: {e}")
            self.results["tests"]["cloud_sync"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_dashboard(self):
        """Test dashboard functionality"""
        try:
            # Test session list
            response = requests.get(
                f"{self.base_url}/api/sessions",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            
            self.results["tests"]["dashboard"] = {
                "status": "success",
                "sessions": response.json()
            }
        except Exception as e:
            logger.error(f"Dashboard test failed: {e}")
            self.results["tests"]["dashboard"] = {
                "status": "error",
                "error": str(e)
            }

    def save_results(self):
        """Save test results to file"""
        os.makedirs("test_results", exist_ok=True)
        filename = f"test_results/e2e_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Test results saved to {filename}")

if __name__ == "__main__":
    test = ScrollIntelE2ETest()
    asyncio.run(test.run_all_tests()) 