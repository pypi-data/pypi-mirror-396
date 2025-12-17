"""Command-line interface for git-reporter."""

import asyncio
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .config import ConfigManager
from .models import AIProvider, ReportPeriod, ReportRequest, RepositoryConfig
from .report_generator import ReportGenerator

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Git Reporter - AI-Powered Git Commit History Analyzer and Report Generator.

    Analyze your git commit history and generate professional reports using AI.
    """
    pass


@main.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(path_type=Path),
    help="Path to configuration file",
)
def init(config: Optional[Path]):
    """Initialize git-reporter configuration."""
    try:
        config_manager = ConfigManager(config)

        if config_manager.config_path.exists():
            if not click.confirm(
                f"Configuration file already exists at {config_manager.config_path}. Overwrite?"
            ):
                console.print("[yellow]Initialization cancelled.[/yellow]")
                return

        # Create default configuration
        config_manager.create_default()

        console.print(
            f"[green]✓[/green] Created configuration file at: {config_manager.config_path}"
        )
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"1. Edit the configuration file: {config_manager.config_path}")
        console.print("2. Add your git repositories")
        console.print("3. Set your AI provider API key as an environment variable:")
        console.print("   - For OpenAI: export OPENAI_API_KEY='your-key'")
        console.print("   - For Gemini: export GEMINI_API_KEY='your-key'")
        console.print("4. Run: git-reporter generate")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(path_type=Path),
    help="Path to configuration file",
)
@click.option("--name", "-n", required=True, help="Repository name")
@click.option("--path", "-p", help="Local path to repository")
@click.option("--repo", "-r", help="Remote repository URL")
@click.option("--email", "-e", help="Filter commits by author email")
def add_repo(
    config: Optional[Path],
    name: str,
    path: Optional[str],
    repo: Optional[str],
    email: Optional[str],
):
    """Add a repository to the configuration.

    Specify either --path for a local repository or --repo for a remote repository.
    """
    try:
        # Validate that either path or repo is provided
        if not path and not repo:
            console.print(
                "[red]Error:[/red] Either --path or --repo must be specified."
            )
            sys.exit(1)

        if path and repo:
            console.print(
                "[red]Error:[/red] Cannot specify both --path and --repo. Use one or the other."
            )
            sys.exit(1)

        config_manager = ConfigManager(config)
        config_obj = config_manager.load()

        # Check if repository already exists
        if any(r.name == name for r in config_obj.repos):
            console.print(
                f"[yellow]Warning:[/yellow] Repository '{name}' already exists."
            )
            if not click.confirm("Overwrite?"):
                console.print("[yellow]Cancelled.[/yellow]")
                return

            # Remove existing
            config_obj.repos = [r for r in config_obj.repos if r.name != name]

        # Add new repository
        repo_config = RepositoryConfig(
            name=name, path=path, repo=repo, author_email=email
        )
        config_obj.repos.append(repo_config)

        config_manager.save(config_obj)

        location_type = "local path" if path else "remote URL"
        location_value = path if path else repo
        console.print(
            f"[green]✓[/green] Added repository: {name} ({location_type}: {location_value})"
        )

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("Run 'git-reporter init' first.")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(path_type=Path),
    help="Path to configuration file",
)
def list_repos(config: Optional[Path]):
    """List configured repositories."""
    try:
        config_manager = ConfigManager(config)
        config_obj = config_manager.load()

        if not config_obj.repos:
            console.print("[yellow]No repositories configured.[/yellow]")
            console.print("Run 'git-reporter add-repo' to add repositories.")
            return

        table = Table(title="Configured Repositories")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Location", style="green")
        table.add_column("Author Email", style="yellow")

        for repo in config_obj.repos:
            repo_type = "Local" if repo.path else "Remote"
            location = repo.path if repo.path else repo.repo
            table.add_row(repo.name, repo_type, location, repo.author_email or "")

        console.print(table)

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(path_type=Path),
    help="Path to configuration file",
)
@click.option(
    "--period",
    "-p",
    type=click.Choice(["daily", "weekly", "monthly", "quarterly", "yearly", "custom"]),
    default="weekly",
    help="Report period",
)
@click.option("--start", "-s", help="Start date for custom period (YYYY-MM-DD)")
@click.option("--end", "-e", help="End date for custom period (YYYY-MM-DD)")
@click.option("--repo", "-r", multiple=True, help="Specific repositories to include")
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output file path"
)
@click.option(
    "--provider",
    type=click.Choice(["openai", "gemini"]),
    help="AI provider to use (overrides config)",
)
def generate(
    config: Optional[Path],
    period: str,
    start: Optional[str],
    end: Optional[str],
    repo: tuple[str],
    output: Optional[Path],
    provider: Optional[str],
):
    """Generate a report from git commit history."""
    try:
        config_manager = ConfigManager(config)
        config_obj = config_manager.load()

        # Override provider if specified
        if provider:
            config_obj.ai_provider = AIProvider(provider)

        # Parse dates for custom period
        start_date = None
        end_date = None
        if period == "custom":
            if not start or not end:
                console.print(
                    "[red]Error:[/red] Custom period requires --start and --end dates."
                )
                sys.exit(1)
            try:
                start_date = datetime.strptime(start, "%Y-%m-%d")
                end_date = datetime.strptime(end, "%Y-%m-%d")
            except ValueError as e:
                console.print(f"[red]Error:[/red] Invalid date format: {e}")
                console.print("Use YYYY-MM-DD format.")
                sys.exit(1)

        # Create report request
        request = ReportRequest(
            period=ReportPeriod(period),
            start_date=start_date,
            end_date=end_date,
            repositories=list(repo) if repo else None,
        )

        # Generate report
        console.print("[cyan]Analyzing commit history...[/cyan]")
        generator = ReportGenerator(config_manager)

        # Run async generate function
        report = asyncio.run(generator.generate(request))

        # Display report
        console.print("\n")
        console.print(
            Panel(
                f"[bold]{request.period.value.upper()} REPORT[/bold]\n"
                f"Period: {report.start_date.strftime('%Y-%m-%d')} to {report.end_date.strftime('%Y-%m-%d')}\n"
                f"Commits: {len(report.commits)}\n"
                f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
                style="bold cyan",
            )
        )

        console.print("\n[bold]Summary:[/bold]\n")
        console.print(Markdown(report.summary))

        # Save to file if requested
        if output:
            output_text = f"""# {request.period.value.upper()} Report

Period: {report.start_date.strftime("%Y-%m-%d")} to {report.end_date.strftime("%Y-%m-%d")}
Commits: {len(report.commits)}
Generated: {report.generated_at.strftime("%Y-%m-%d %H:%M:%S")}

## Summary

{report.summary}

## Commit Details

"""
            for commit in report.commits:
                output_text += f"- [{commit.repository}] {commit.date.strftime('%Y-%m-%d %H:%M')}: {commit.message[:100]}\n"

            output.write_text(output_text)
            console.print(f"\n[green]✓[/green] Report saved to: {output}")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
