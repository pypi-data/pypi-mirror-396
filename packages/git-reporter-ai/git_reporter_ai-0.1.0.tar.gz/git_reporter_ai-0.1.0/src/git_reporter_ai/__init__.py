"""Git Reporter - AI-Powered Git Commit History Analyzer and Report Generator."""

__version__ = "0.1.0"

from .cli import main
from .config import ConfigManager
from .git_analyzer import GitAnalyzer
from .models import (
    AIProvider,
    Config,
    GitCommit,
    Report,
    ReportPeriod,
    ReportRequest,
    RepositoryConfig,
)
from .report_generator import ReportGenerator

__all__ = [
    "main",
    "ConfigManager",
    "GitAnalyzer",
    "ReportGenerator",
    "AIProvider",
    "Config",
    "GitCommit",
    "Report",
    "ReportPeriod",
    "ReportRequest",
    "RepositoryConfig",
]
