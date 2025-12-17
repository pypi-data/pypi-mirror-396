"""Report generator that coordinates git analysis and AI generation."""

from datetime import datetime, timedelta
from typing import Optional

from .ai import GeminiProvider, OpenAIProvider
from .config import ConfigManager
from .git_analyzer import GitAnalyzer
from .models import AIProvider, Report, ReportPeriod, ReportRequest


class ReportGenerator:
    """Generates reports from git commit history using AI."""

    def __init__(self, config_manager: ConfigManager):
        """Initialize the report generator.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.load()

    def _get_date_range(
        self,
        period: ReportPeriod,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[datetime, datetime]:
        """Calculate date range for a given period.

        Args:
            period: Report period
            start_date: Override start date
            end_date: Override end date

        Returns:
            Tuple of (start_date, end_date)
        """
        now = datetime.now()

        if period == ReportPeriod.CUSTOM:
            if not start_date or not end_date:
                raise ValueError("Custom period requires both start_date and end_date")
            return start_date, end_date

        elif period == ReportPeriod.DAILY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now

        elif period == ReportPeriod.WEEKLY:
            # Start from Monday of current week
            days_since_monday = now.weekday()
            start = (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end = now

        elif period == ReportPeriod.MONTHLY:
            # Start from first day of current month
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now

        elif period == ReportPeriod.QUARTERLY:
            # Start from first day of current quarter
            current_quarter = (now.month - 1) // 3
            quarter_start_month = current_quarter * 3 + 1
            start = now.replace(
                month=quarter_start_month,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            end = now

        elif period == ReportPeriod.YEARLY:
            # Start from first day of current year
            start = now.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end = now

        else:
            raise ValueError(f"Unknown period: {period}")

        return start, end

    async def generate(self, request: ReportRequest) -> Report:
        """Generate a report based on the request.

        Args:
            request: Report request

        Returns:
            Generated report

        Raises:
            ValueError: If configuration is invalid
        """
        # Get date range
        start_date, end_date = self._get_date_range(
            request.period, request.start_date, request.end_date
        )

        # Collect commits from all configured repositories
        all_commits = []
        repos_to_analyze = request.repositories or [r.name for r in self.config.repos]

        for repo_config in self.config.repos:
            if repo_config.name not in repos_to_analyze:
                continue

            try:
                analyzer = GitAnalyzer(repo_config)
                commits = analyzer.get_commits(
                    start_date=start_date,
                    end_date=end_date,
                    author_email=repo_config.author_email,
                )
                all_commits.extend(commits)
                # Clean up temporary directories for remote repos
                analyzer.cleanup()
            except Exception as e:
                # Log error but continue with other repos
                import sys

                print(
                    f"Warning: Error analyzing {repo_config.name}: {e}", file=sys.stderr
                )

        # Sort all commits by date
        all_commits.sort(key=lambda c: c.date, reverse=True)

        # Generate AI summary
        summary = await self._generate_summary(all_commits, request.period)

        return Report(
            period=request.period,
            start_date=start_date,
            end_date=end_date,
            commits=all_commits,
            summary=summary,
        )

    async def _generate_summary(self, commits: list, period: ReportPeriod) -> str:
        """Generate AI summary of commits.

        Args:
            commits: List of commits
            period: Report period

        Returns:
            AI-generated summary
        """
        if not commits:
            return "No commits found in this period."

        # Initialize AI provider
        if self.config.ai_provider == AIProvider.OPENAI:
            if not self.config.openai_api_key:
                raise ValueError(
                    "OpenAI API key not configured. Set OPENAI_API_KEY environment variable "
                    "or add 'openai_api_key' to config."
                )
            provider = OpenAIProvider(
                api_key=self.config.openai_api_key,
                model=self.config.openai_model,
            )
        elif self.config.ai_provider == AIProvider.GEMINI:
            if not self.config.gemini_api_key:
                raise ValueError(
                    "Gemini API key not configured. Set GEMINI_API_KEY environment variable "
                    "or add 'gemini_api_key' to config."
                )
            provider = GeminiProvider(
                api_key=self.config.gemini_api_key,
                model=self.config.gemini_model,
            )
        else:
            raise ValueError(f"Unknown AI provider: {self.config.ai_provider}")

        return await provider.generate_report(commits, period)
