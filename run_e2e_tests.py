"""
Run ScrollIntel v2 End-to-End Tests
"""

import os
import asyncio
from dotenv import load_dotenv
from tests.e2e_test import ScrollIntelE2ETest

async def main():
    # Load environment variables
    load_dotenv()
    
    # Verify required credentials
    required_vars = [
        "OPENAI_API_KEY",
        "DROPBOX_ACCESS_TOKEN",
        "GA4_CLIENT_ID",
        "GA4_CLIENT_SECRET",
        "GA4_PROPERTY_ID",
        "GITHUB_TOKEN"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return
    
    # Initialize and run tests
    test_suite = ScrollIntelE2ETest()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 