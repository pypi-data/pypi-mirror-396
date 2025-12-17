"""Base AI provider interface."""

from abc import ABC, abstractmethod
from typing import Optional

from ..models import GitCommit, ReportPeriod


class AIProvider(ABC):
    """Base class for AI providers."""

    @abstractmethod
    async def generate_report(
        self,
        commits: list[GitCommit],
        period: ReportPeriod,
        additional_context: Optional[str] = None,
    ) -> str:
        """Generate a report summary from commits.

        Args:
            commits: List of commits to summarize
            period: Report period
            additional_context: Optional additional context

        Returns:
            Generated report text
        """
        pass

    def _format_commits_for_prompt(self, commits: list[GitCommit]) -> str:
        """Format commits into a readable format for the AI prompt.

        Args:
            commits: List of commits

        Returns:
            Formatted string
        """
        if not commits:
            return "No commits found in this period."

        lines = []
        for commit in commits:
            lines.append(
                f"- [{commit.repository}] {commit.date.strftime('%Y-%m-%d %H:%M')}: "
                f"{commit.message[:100]} "
                f"(+{commit.insertions}/-{commit.deletions}, {commit.files_changed} files)"
            )

        return "\n".join(lines)

    def _create_system_prompt(self, period: ReportPeriod) -> str:
        """Create the system prompt for the AI.

        Args:
            period: Report period

        Returns:
            System prompt
        """
        return (
            f"You are a helpful assistant that creates concise, professional {period.value} "
            f"work reports based on git commit history. Your reports should:\n"
            f"1. Summarize the main accomplishments and work done\n"
            f"2. Group related commits into logical themes or projects\n"
            f"3. Highlight significant changes, features, or bug fixes\n"
            f"4. Be written in a professional tone suitable for a manager\n"
            f"5. Focus on what was achieved, not just listing commits\n"
            f"6. Be structured with clear sections and bullet points\n"
        )
