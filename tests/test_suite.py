"""
ScrollIntel v2 Test Suite
Comprehensive testing of all core functionalities
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
import pytz
from pathlib import Path
import requests
from dotenv import load_dotenv
import pandas as pd
import wave
import contextlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_suite.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScrollIntelTestSuite:
    def __init__(self):
        """Initialize test suite."""
        load_dotenv()
        self.base_url = "http://localhost:8000"
        self.token = None
        self.test_session_id = None
        self.test_results = {
            "start_time": datetime.now(pytz.UTC).isoformat(),
            "components": {},
            "errors": [],
            "recommendations": []
        }
        
        # Create test directories
        self.test_dirs = {
            "voice": Path("test_data/voice"),
            "charts": Path("test_data/charts"),
            "exports": Path("test_data/exports")
        }
        for dir_path in self.test_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

    async def run_all_tests(self):
        """Run all test components."""
        try:
            # 1. Test OpenAI Integration
            await self.test_openai_integration()
            
            # 2. Test Whisper Voice Transcription
            await self.test_whisper_transcription()
            
            # 3. Test Google Sheets Integration
            await self.test_google_sheets()
            
            # 4. Test Dropbox Integration
            await self.test_dropbox_integration()
            
            # 5. Test GA4 Integration
            await self.test_ga4_integration()
            
            # 6. Test GitHub Export
            await self.test_github_export()
            
            # 7. Test Cloud Sync
            await self.test_cloud_sync()
            
            # 8. Test PDF Export
            await self.test_pdf_export()
            
            # 9. Test Dashboard
            await self.test_dashboard()
            
            # Log final results
            self.test_results["end_time"] = datetime.now(pytz.UTC).isoformat()
            self._save_test_results()
            self._generate_test_log()
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            self.test_results["errors"].append(str(e))
            self._save_test_results()
            self._generate_test_log()

    async def test_openai_integration(self):
        """Test OpenAI GPT integration and ScrollProphet endpoints."""
        logger.info("Testing OpenAI Integration...")
        
        try:
            # Test insights endpoint
            insights_response = requests.post(
                f"{self.base_url}/prophet/insights",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "context": {
                        "domain": "test_domain",
                        "data_type": "test_data",
                        "metrics": ["test_metric"]
                    }
                }
            )
            insights_response.raise_for_status()
            insights_data = insights_response.json()
            
            # Validate response structure
            assert "insights" in insights_data
            assert "scroll_caption" in insights_data
            assert "scroll_seal" in insights_data
            
            self.test_results["components"]["openai"] = {
                "status": "success",
                "insights": insights_data
            }
            
            logger.info("OpenAI Integration test passed")
            
        except Exception as e:
            logger.error(f"OpenAI Integration test failed: {e}")
            self.test_results["components"]["openai"] = {
                "status": "failed",
                "error": str(e)
            }
            raise

    async def test_whisper_transcription(self):
        """Test Whisper voice transcription."""
        logger.info("Testing Whisper Transcription...")
        
        try:
            # Create a test WAV file
            test_wav = self.test_dirs["voice"] / "test_voice.wav"
            self._create_test_wav(test_wav)
            
            # Upload and transcribe
            with open(test_wav, "rb") as f:
                files = {"file": ("test_voice.wav", f, "audio/wav")}
                response = requests.post(
                    f"{self.base_url}/voice",
                    headers={"Authorization": f"Bearer {self.token}"},
                    files=files
                )
            response.raise_for_status()
            
            # Validate response
            result = response.json()
            assert "transcription" in result
            assert "interpretation" in result
            assert "scroll_caption" in result
            
            self.test_results["components"]["whisper"] = {
                "status": "success",
                "transcription": result
            }
            
            logger.info("Whisper Transcription test passed")
            
        except Exception as e:
            logger.error(f"Whisper Transcription test failed: {e}")
            self.test_results["components"]["whisper"] = {
                "status": "failed",
                "error": str(e)
            }
            raise

    async def test_google_sheets(self):
        """Test Google Sheets integration."""
        logger.info("Testing Google Sheets Integration...")
        
        try:
            # Test sheets integration
            sheets_response = requests.post(
                f"{self.base_url}/integrate/sheets",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "sheet_url": os.getenv("TEST_SHEET_URL"),
                    "sheet_name": "Sheet1"
                }
            )
            sheets_response.raise_for_status()
            
            # Validate response
            result = sheets_response.json()
            assert "session_id" in result
            assert "interpretation" in result
            assert "scroll_caption" in result
            
            self.test_session_id = result["session_id"]
            
            self.test_results["components"]["google_sheets"] = {
                "status": "success",
                "session_id": self.test_session_id,
                "interpretation": result["interpretation"]
            }
            
            logger.info("Google Sheets Integration test passed")
            
        except Exception as e:
            logger.error(f"Google Sheets Integration test failed: {e}")
            self.test_results["components"]["google_sheets"] = {
                "status": "failed",
                "error": str(e)
            }
            raise

    async def test_dropbox_integration(self):
        """Test Dropbox integration."""
        logger.info("Testing Dropbox Integration...")
        
        try:
            # List files
            dropbox_response = requests.post(
                f"{self.base_url}/integrate/dropbox",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "path": "/ScrollIntel/auto/",
                    "file_types": [".csv", ".xlsx"]
                }
            )
            dropbox_response.raise_for_status()
            
            files = dropbox_response.json()["files"]
            if not files:
                raise ValueError("No files found in Dropbox auto-sync folder")
            
            # Read and interpret file
            test_file = next(f for f in files if f["name"].endswith(('.csv', '.xlsx')))
            interpret_response = requests.post(
                f"{self.base_url}/integrate/dropbox/read",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "path": test_file["path"],
                    "file_type": test_file["name"].split('.')[-1]
                }
            )
            interpret_response.raise_for_status()
            
            result = interpret_response.json()
            assert "session_id" in result
            assert "interpretation" in result
            assert "scroll_caption" in result
            
            self.test_session_id = result["session_id"]
            
            self.test_results["components"]["dropbox"] = {
                "status": "success",
                "session_id": self.test_session_id,
                "interpretation": result["interpretation"]
            }
            
            logger.info("Dropbox Integration test passed")
            
        except Exception as e:
            logger.error(f"Dropbox Integration test failed: {e}")
            self.test_results["components"]["dropbox"] = {
                "status": "failed",
                "error": str(e)
            }
            raise

    async def test_ga4_integration(self):
        """Test Google Analytics 4 integration."""
        logger.info("Testing GA4 Integration...")
        
        try:
            # Test GA4 integration
            ga4_response = requests.post(
                f"{self.base_url}/integrate/ga4",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "property_id": os.getenv("GA4_PROPERTY_ID"),
                    "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "end_date": datetime.now().strftime("%Y-%m-%d")
                }
            )
            ga4_response.raise_for_status()
            
            result = ga4_response.json()
            assert "session_id" in result
            assert "interpretation" in result
            assert "scroll_caption" in result
            
            self.test_session_id = result["session_id"]
            
            self.test_results["components"]["ga4"] = {
                "status": "success",
                "session_id": self.test_session_id,
                "interpretation": result["interpretation"]
            }
            
            logger.info("GA4 Integration test passed")
            
        except Exception as e:
            logger.error(f"GA4 Integration test failed: {e}")
            self.test_results["components"]["ga4"] = {
                "status": "failed",
                "error": str(e)
            }
            raise

    async def test_github_export(self):
        """Test GitHub repository creation and file push."""
        logger.info("Testing GitHub Export...")
        
        try:
            if not self.test_session_id:
                raise ValueError("No test session available")
            
            # Push to GitHub
            github_response = requests.post(
                f"{self.base_url}/export/github/{self.test_session_id}",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "repo_name": f"scrollintel-test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "commit_message": "ScrollIntel Test Push"
                }
            )
            github_response.raise_for_status()
            
            result = github_response.json()
            assert "commit_url" in result
            assert "repo_url" in result
            
            self.test_results["components"]["github_export"] = {
                "status": "success",
                "commit_url": result["commit_url"],
                "repo_url": result["repo_url"]
            }
            
            logger.info("GitHub Export test passed")
            
        except Exception as e:
            logger.error(f"GitHub Export test failed: {e}")
            self.test_results["components"]["github_export"] = {
                "status": "failed",
                "error": str(e)
            }
            raise

    async def test_cloud_sync(self):
        """Test cloud sync functionality."""
        logger.info("Testing Cloud Sync...")
        
        try:
            # Trigger manual sync
            sync_response = requests.post(
                f"{self.base_url}/sync/cloud",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            sync_response.raise_for_status()
            
            # Get sync status
            status_response = requests.get(
                f"{self.base_url}/sync/status",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            status_response.raise_for_status()
            
            sync_result = sync_response.json()
            status_result = status_response.json()
            
            assert "processed_files" in sync_result
            assert "new_sessions" in sync_result
            assert "last_sync" in status_result
            
            self.test_results["components"]["cloud_sync"] = {
                "status": "success",
                "sync_result": sync_result,
                "sync_status": status_result
            }
            
            logger.info("Cloud Sync test passed")
            
        except Exception as e:
            logger.error(f"Cloud Sync test failed: {e}")
            self.test_results["components"]["cloud_sync"] = {
                "status": "failed",
                "error": str(e)
            }
            raise

    async def test_pdf_export(self):
        """Test PDF report generation."""
        logger.info("Testing PDF Export...")
        
        try:
            if not self.test_session_id:
                raise ValueError("No test session available")
            
            # Generate PDF report
            pdf_response = requests.post(
                f"{self.base_url}/export/pdf/{self.test_session_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            pdf_response.raise_for_status()
            
            result = pdf_response.json()
            assert "file_path" in result
            
            # Verify PDF file exists
            pdf_path = result["file_path"]
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            self.test_results["components"]["pdf_export"] = {
                "status": "success",
                "file_path": pdf_path
            }
            
            logger.info("PDF Export test passed")
            
        except Exception as e:
            logger.error(f"PDF Export test failed: {e}")
            self.test_results["components"]["pdf_export"] = {
                "status": "failed",
                "error": str(e)
            }
            raise

    async def test_dashboard(self):
        """Test dashboard functionality."""
        logger.info("Testing Dashboard...")
        
        try:
            # Get integrations
            integrations_response = requests.get(
                f"{self.base_url}/integrations",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            integrations_response.raise_for_status()
            
            # Get sessions
            sessions_response = requests.get(
                f"{self.base_url}/sessions",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            sessions_response.raise_for_status()
            
            integrations_data = integrations_response.json()
            sessions_data = sessions_response.json()
            
            assert "integrations" in integrations_data
            assert "sessions" in sessions_data
            
            self.test_results["components"]["dashboard"] = {
                "status": "success",
                "integrations": integrations_data,
                "sessions": sessions_data
            }
            
            logger.info("Dashboard test passed")
            
        except Exception as e:
            logger.error(f"Dashboard test failed: {e}")
            self.test_results["components"]["dashboard"] = {
                "status": "failed",
                "error": str(e)
            }
            raise

    def _create_test_wav(self, file_path):
        """Create a test WAV file."""
        with wave.open(file_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            wav_file.writeframes(b'\x00' * 44100)  # 1 second of silence

    def _save_test_results(self):
        """Save test results to file."""
        results_path = Path("test_results")
        results_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_path / f"test_results_{timestamp}.json"
        
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Test results saved to {results_file}")

    def _generate_test_log(self):
        """Generate test log in markdown format."""
        log_path = Path("test_log.md")
        
        with open(log_path, "w") as f:
            f.write("# ScrollIntel v2 Test Results\n\n")
            f.write(f"Test run: {self.test_results['start_time']}\n\n")
            
            f.write("## Component Status\n\n")
            for component, result in self.test_results["components"].items():
                status = "✅ PASSED" if result["status"] == "success" else "❌ FAILED"
                f.write(f"### {component.title()}\n")
                f.write(f"- Status: {status}\n")
                if result["status"] == "failed":
                    f.write(f"- Error: {result['error']}\n")
                f.write("\n")
            
            if self.test_results["errors"]:
                f.write("## Errors\n\n")
                for error in self.test_results["errors"]:
                    f.write(f"- {error}\n")
                f.write("\n")
            
            if self.test_results["recommendations"]:
                f.write("## Recommendations\n\n")
                for rec in self.test_results["recommendations"]:
                    f.write(f"- {rec}\n")
                f.write("\n")
        
        logger.info(f"Test log generated at {log_path}")

if __name__ == "__main__":
    # Run tests
    test_suite = ScrollIntelTestSuite()
    asyncio.run(test_suite.run_all_tests()) 