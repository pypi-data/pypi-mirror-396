"""Git repository management."""

import os
import subprocess
from pathlib import Path
from typing import Optional

from jobrunner.config import ConfigLoader
from jobrunner.exceptions import GitError
from jobrunner.models import Job, Repository


class GitManager:
    """Manages Git repository operations."""

    def __init__(self, config: ConfigLoader, verbose: bool = False) -> None:
        """Initialize Git manager.
        
        Args:
            config: Configuration loader instance
            verbose: Enable verbose output
        """
        self.config = config
        self.verbose = verbose
        self.current_depth = 0  # Track current depth for indentation

    def ensure_repository(self, job_name: str, job: Job) -> None:
        """Ensure repository is cloned and at correct version.
        
        Args:
            job_name: Name of the job
            job: Job configuration
        """
        if not job.repo:
            return

        repo_path = self.get_repo_path(job)
        
        if not (repo_path / ".git").exists():
            self._clone_repository(job)
        
        if job.repo.version_ref:
            self._checkout_version(repo_path, job.repo.version_ref)

    def get_repo_path(self, job: Job) -> Path:
        """Get the local path for a repository."""
        if not job.repo or not job.directory:
            raise GitError("Job missing repository or directory configuration")
        
        repo_name = Path(job.repo.name).stem
        return Path(job.directory) / job.repo.group / repo_name

    def _clone_repository(self, job: Job) -> None:
        """Clone a Git repository."""
        if not job.repo:
            return

        repo_url = f"{job.repo.server}{job.repo.group}{job.repo.name}"
        repo_path = self.get_repo_path(job)
        
        # Create parent directory
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.verbose:
            print(f"Cloning {repo_url}...")
        else:
            indent = "  " * (self.current_depth + 1)
            print(f"{indent}Fetching {repo_url}")
        
        result = subprocess.run(
            ["git", "clone", repo_url, str(repo_path)],
            capture_output=not self.verbose,
            text=True
        )
        
        if result.returncode != 0:
            raise GitError(f"Failed to clone repository: {repo_url}")

    def _checkout_version(self, repo_path: Path, version_ref: str) -> None:
        """Checkout a specific version of the repository."""
        if self.verbose:
            print(f"Checking out {version_ref}...")
        
        result = subprocess.run(
            ["git", "checkout", version_ref],
            cwd=repo_path,
            capture_output=not self.verbose,
            text=True
        )
        
        if result.returncode != 0:
            raise GitError(f"Failed to checkout {version_ref}")
