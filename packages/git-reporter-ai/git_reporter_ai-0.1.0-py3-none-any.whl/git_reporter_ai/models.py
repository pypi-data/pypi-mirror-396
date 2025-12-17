"""Data models for git-reporter."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ReportPeriod(str, Enum):
    """Report time period options."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class AIProvider(str, Enum):
    """Supported AI providers."""

    OPENAI = "openai"
    GEMINI = "gemini"


class GitCommit(BaseModel):
    """Represents a git commit."""

    sha: str = Field(..., description="Commit SHA hash")
    author: str = Field(..., description="Commit author name")
    email: str = Field(..., description="Commit author email")
    date: datetime = Field(..., description="Commit timestamp")
    message: str = Field(..., description="Commit message")
    repository: str = Field(..., description="Repository name")
    files_changed: int = Field(default=0, description="Number of files changed")
    insertions: int = Field(default=0, description="Number of insertions")
    deletions: int = Field(default=0, description="Number of deletions")


class RepositoryConfig(BaseModel):
    """Configuration for a single repository."""

    name: str = Field(..., description="Repository name")
    path: Optional[str] = Field(None, description="Local path to repository")
    repo: Optional[str] = Field(None, description="Remote repository URL")
    author_email: Optional[str] = Field(
        None, description="Filter commits by author email"
    )

    def get_repo_location(self) -> str:
        """Get the repository location (either local path or remote URL)."""
        if self.path:
            return self.path
        elif self.repo:
            return self.repo
        else:
            raise ValueError(
                f"Repository '{self.name}' must have either 'path' or 'repo' specified"
            )


class Config(BaseModel):
    """Main configuration for git-reporter."""

    model_config = {"populate_by_name": True}  # Allow both field name and alias

    repos: list[RepositoryConfig] = Field(
        default_factory=list,
        description="List of repositories to analyze",
        alias="repositories",  # Support both 'repos' and 'repositories' for backwards compatibility
    )
    ai_provider: AIProvider = Field(
        default=AIProvider.OPENAI, description="AI provider to use"
    )
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    gemini_api_key: Optional[str] = Field(None, description="Google Gemini API key")
    gemini_model: str = Field(
        default="gemini-2.0-flash-exp", description="Gemini model to use"
    )
    default_period: ReportPeriod = Field(
        default=ReportPeriod.WEEKLY, description="Default report period"
    )


class ReportRequest(BaseModel):
    """Request for generating a report."""

    period: ReportPeriod = Field(..., description="Report time period")
    start_date: Optional[datetime] = Field(
        None, description="Start date for custom period"
    )
    end_date: Optional[datetime] = Field(None, description="End date for custom period")
    repositories: Optional[list[str]] = Field(
        None, description="Specific repositories to include (None = all)"
    )


class Report(BaseModel):
    """Generated report."""

    period: ReportPeriod = Field(..., description="Report period")
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    commits: list[GitCommit] = Field(..., description="Commits in this period")
    summary: str = Field(..., description="AI-generated summary")
    generated_at: datetime = Field(
        default_factory=datetime.now, description="When the report was generated"
    )
