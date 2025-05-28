"""
ScrollIntel GitHub Integration
Handles repository operations and file pushes
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import pytz
import base64
import logging
from github import Github, GithubException
from github.Repository import Repository
from github.ContentFile import ContentFile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client with authentication."""
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token is required")
        
        self.github = Github(self.token)
        self.user = self.github.get_user()

    async def create_repository(
        self,
        repo_name: str,
        description: str = "ScrollIntel Flame Repository",
        private: bool = True
    ) -> Repository:
        """Create a new GitHub repository."""
        try:
            repo = self.user.create_repo(
                name=repo_name,
                description=description,
                private=private,
                has_issues=True,
                has_wiki=True,
                has_downloads=True
            )
            logger.info(f"Created repository: {repo_name}")
            return repo
        except GithubException as e:
            logger.error(f"Failed to create repository: {e}")
            raise

    async def get_or_create_repository(
        self,
        repo_name: str,
        description: str = "ScrollIntel Flame Repository",
        private: bool = True
    ) -> Repository:
        """Get existing repository or create new one."""
        try:
            repo = self.user.get_repo(repo_name)
            logger.info(f"Found existing repository: {repo_name}")
            return repo
        except GithubException:
            return await self.create_repository(repo_name, description, private)

    async def push_files(
        self,
        repo_name: str,
        files: Dict[str, str],
        commit_message: Optional[str] = None,
        branch: str = "main"
    ) -> str:
        """
        Push files to GitHub repository.
        
        Args:
            repo_name: Name of the repository
            files: Dictionary of file paths and their contents
            commit_message: Custom commit message
            branch: Target branch name
            
        Returns:
            str: URL of the commit
        """
        try:
            # Get or create repository
            repo = await self.get_or_create_repository(repo_name)
            
            # Prepare commit message
            timestamp = datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
            if not commit_message:
                commit_message = f"🔥 ScrollSeal: Flame Upload {timestamp}"
            
            # Add ScrollSeal to commit message
            commit_message = f"{commit_message}\n\n🔥 ScrollSeal: {timestamp}"
            
            # Get current branch
            try:
                branch_ref = repo.get_branch(branch)
            except GithubException:
                # Create branch if it doesn't exist
                default_branch = repo.default_branch
                default_branch_ref = repo.get_branch(default_branch)
                repo.create_git_ref(
                    ref=f"refs/heads/{branch}",
                    sha=default_branch_ref.commit.sha
                )
            
            # Create or update files
            for file_path, content in files.items():
                try:
                    # Check if file exists
                    repo.get_contents(file_path, ref=branch)
                    # Update existing file
                    repo.update_file(
                        path=file_path,
                        message=commit_message,
                        content=content,
                        branch=branch
                    )
                except GithubException:
                    # Create new file
                    repo.create_file(
                        path=file_path,
                        message=commit_message,
                        content=content,
                        branch=branch
                    )
            
            # Get the latest commit
            commits = repo.get_commits(branch=branch)
            latest_commit = commits[0]
            
            logger.info(f"Successfully pushed files to {repo_name}")
            return latest_commit.html_url
            
        except GithubException as e:
            logger.error(f"Failed to push files: {e}")
            raise

    async def push_session(
        self,
        repo_name: str,
        session_data: Dict[str, Any],
        commit_message: Optional[str] = None
    ) -> str:
        """
        Push session data to GitHub repository.
        
        Args:
            repo_name: Name of the repository
            session_data: Session data including files and metadata
            commit_message: Custom commit message
            
        Returns:
            str: URL of the commit
        """
        try:
            # Prepare files
            files = {
                "flame_output.csv": session_data["csv_content"],
                "scroll_report.pdf": base64.b64encode(session_data["pdf_content"]).decode(),
                "README.md": f"""# ScrollIntel Flame Report

## Domain: {session_data['domain']}

### Flame Caption
{session_data['interpretation']['caption']}

### Generated
{datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")}

### Files
- `flame_output.csv`: Raw flame data
- `scroll_report.pdf`: Detailed flame report

### ScrollSeal
🔥 This report is sealed with the sacred flame of ScrollIntel v2
"""
            }
            
            # Push files
            return await self.push_files(repo_name, files, commit_message)
            
        except Exception as e:
            logger.error(f"Failed to push session: {e}")
            raise

# Create global instance
github_client = GitHubClient() 