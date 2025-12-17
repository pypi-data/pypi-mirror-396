"""Git repository analyzer."""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

from .models import GitCommit, RepositoryConfig


class GitAnalyzer:
    """Analyzes git repositories and extracts commit history."""

    def __init__(self, repo_config: RepositoryConfig):
        """Initialize the analyzer with a repository configuration.

        Args:
            repo_config: Repository configuration

        Raises:
            InvalidGitRepositoryError: If the path is not a valid git repository
        """
        self.config = repo_config
        self.is_temporary = False
        self.temp_dir = None

        # Handle remote repositories
        if repo_config.repo and not repo_config.path:
            # Clone remote repository to a temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix=f"git-reporter-{repo_config.name}-")
            self.repo_path = Path(self.temp_dir)
            self.is_temporary = True

            try:
                print(f"Cloning remote repository: {repo_config.repo}")
                self.repo = Repo.clone_from(
                    repo_config.repo, self.repo_path, depth=None
                )
            except Exception as e:
                # Clean up temp directory if clone fails
                if self.temp_dir and Path(self.temp_dir).exists():
                    shutil.rmtree(self.temp_dir)
                raise RuntimeError(
                    f"Failed to clone repository {repo_config.repo}: {e}"
                ) from e
        else:
            # Handle local repositories
            self.repo_path = Path(repo_config.path).expanduser().resolve()

            if not self.repo_path.exists():
                raise FileNotFoundError(f"Repository path not found: {self.repo_path}")

            try:
                self.repo = Repo(self.repo_path)
            except InvalidGitRepositoryError as e:
                raise InvalidGitRepositoryError(
                    f"Not a valid git repository: {self.repo_path}"
                ) from e

    def cleanup(self):
        """Clean up temporary directories if created."""
        if self.is_temporary and self.temp_dir and Path(self.temp_dir).exists():
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(
                    f"Warning: Failed to cleanup temporary directory {self.temp_dir}: {e}"
                )

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()

    def get_commits(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        author_email: Optional[str] = None,
    ) -> list[GitCommit]:
        """Get commits from the repository within a date range.

        Args:
            start_date: Start date for filtering commits (inclusive)
            end_date: End date for filtering commits (inclusive)
            author_email: Filter by author email (uses config if not provided)

        Returns:
            List of GitCommit objects
        """
        # Use config author_email if not provided
        if author_email is None:
            author_email = self.config.author_email

        commits = []
        try:
            # Get all commits from all branches
            for commit in self.repo.iter_commits(all=True):
                commit_date = datetime.fromtimestamp(commit.committed_date)

                # Filter by date range
                if start_date and commit_date < start_date:
                    continue
                if end_date and commit_date > end_date:
                    continue

                # Filter by author email
                if author_email and commit.author.email != author_email:
                    continue

                # Get stats
                try:
                    stats = commit.stats.total
                    files_changed = stats.get("files", 0)
                    insertions = stats.get("insertions", 0)
                    deletions = stats.get("deletions", 0)
                except (AttributeError, GitCommandError):
                    files_changed = insertions = deletions = 0

                git_commit = GitCommit(
                    sha=commit.hexsha,
                    author=commit.author.name,
                    email=commit.author.email,
                    date=commit_date,
                    message=commit.message.strip(),
                    repository=self.config.name,
                    files_changed=files_changed,
                    insertions=insertions,
                    deletions=deletions,
                )
                commits.append(git_commit)

        except GitCommandError as e:
            raise RuntimeError(
                f"Error reading commits from {self.config.name}: {e}"
            ) from e

        # Sort by date descending (newest first)
        commits.sort(key=lambda c: c.date, reverse=True)
        return commits

    def get_branch_name(self) -> str:
        """Get the current branch name.

        Returns:
            Current branch name
        """
        try:
            return self.repo.active_branch.name
        except (AttributeError, TypeError):
            return "HEAD"

    def get_remote_url(self) -> Optional[str]:
        """Get the remote URL of the repository.

        Returns:
            Remote URL or None if not available
        """
        try:
            if self.repo.remotes:
                return self.repo.remotes[0].url
        except (AttributeError, IndexError):
            pass
        return None
