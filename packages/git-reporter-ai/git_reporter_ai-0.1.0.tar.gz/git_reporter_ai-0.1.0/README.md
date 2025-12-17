# git-reporter

AI-Powered Git Commit History Analyzer and Report Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## Overview

`git-reporter` is a powerful Python tool that analyzes your Git commit history across multiple repositories and uses AI to generate professional work reports. Perfect for developers who need to create weekly, monthly, quarterly, or yearly reports for their managers without maintaining daily logs.

## 📚 Documentation

Full documentation is available at: **https://shenxianpeng.github.io/git-reporter/**

- [Installation Guide](https://shenxianpeng.github.io/git-reporter/getting-started/installation/)
- [Quick Start](https://shenxianpeng.github.io/git-reporter/getting-started/quickstart/)
- [Configuration](https://shenxianpeng.github.io/git-reporter/getting-started/configuration/)
- [CLI Commands](https://shenxianpeng.github.io/git-reporter/user-guide/cli-commands/)
- [AI Providers](https://shenxianpeng.github.io/git-reporter/user-guide/ai-providers/)

## Features

- 📊 **Multi-Repository Analysis**: Analyze commits from multiple Git repositories simultaneously
- 🌐 **Remote & Local Repos**: Support both local and remote (GitHub, GitLab, etc.) repositories
- 🤖 **AI-Powered Reports**: Generate intelligent summaries using OpenAI GPT or Google Gemini
- ⏰ **Flexible Time Periods**: Support for daily, weekly, monthly, quarterly, yearly, and custom date ranges
- 🎯 **Author Filtering**: Filter commits by specific author email addresses
- 🔧 **Easy Configuration**: Simple YAML-based configuration with local or global config files
- 🎨 **Rich CLI Interface**: Beautiful command-line interface with progress indicators
- 📝 **Export Reports**: Save reports to markdown files
- 🔒 **Secure**: API keys stored in environment variables, not in config files
- 📂 **Local Config Priority**: Project-level `git-reporter.yaml` takes priority over global config

## Technologies Used

- **UV**: Modern Python package manager for fast dependency management
- **Pydantic**: Data validation using Python type annotations
- **Pydantic-AI**: AI model abstraction layer for easy integration with multiple providers
- **GitPython**: Git repository interaction
- **Click**: Command-line interface creation
- **Rich**: Beautiful terminal output

## Installation

### From PyPI (Once Published)

```bash
pip install git-reporter
```

### From Source

```bash
# Clone the repository
git clone https://github.com/shenxianpeng/git-reporter.git
cd git-reporter

# Install UV if you haven't already
pip install uv

# Install the package
uv sync
```

## Quick Start

### 1. Initialize Configuration

```bash
git-reporter init
```

This creates a configuration file at `~/.git-reporter/config.yaml`.

**Or** create a local configuration file in your project directory:
```bash
# Create git-reporter.yaml in current directory
touch git-reporter.yaml
```

**Note:** Local config files (`git-reporter.yaml`, `git-reporter.yml`, `.git-reporter.yaml`, `.git-reporter.yml`) in the current directory take priority over the global config.

### 2. Add Repositories

**For local repositories:**
```bash
git-reporter add-repo --name "my-project" --path "/path/to/repo" --email "your@email.com"
```

**For remote repositories (automatically cloned):**
```bash
git-reporter add-repo --name "github-project" --repo "https://github.com/username/repo.git" --email "your@email.com"
```

### 3. Set Up API Keys

Set your AI provider API key as an environment variable:

```bash
# For OpenAI
export OPENAI_API_KEY='your-openai-api-key'

# Or for Google Gemini
export GEMINI_API_KEY='your-gemini-api-key'
```

### 4. Generate a Report

```bash
# Generate a weekly report (default)
git-reporter generate

# Generate a monthly report
git-reporter generate --period monthly

# Generate a custom period report
git-reporter generate --period custom --start 2024-01-01 --end 2024-12-31

# Save report to file
git-reporter generate --period weekly --output report.md
```

## Configuration

The configuration file can be:
- Global: `~/.git-reporter/config.yaml`
- Local: `git-reporter.yaml` or `git-reporter.yml` in current directory (takes priority)

Here's an example:

```yaml
ai_provider: openai  # or 'gemini'
default_period: weekly
openai_model: gpt-4o-mini
gemini_model: gemini-2.0-flash-exp
repos:  # or 'repositories' (both work)
  # Local repository
  - name: my-project
    path: /home/user/projects/my-project
    author_email: developer@example.com
  
  # Remote repository (auto-cloned when generating reports)
  - name: github-project
    repo: https://github.com/username/repo.git
    author_email: developer@example.com
```

### Configuration Options

- `ai_provider`: AI provider to use (`openai` or `gemini`)
- `default_period`: Default report period (`daily`, `weekly`, `monthly`, `quarterly`, `yearly`)
- `openai_model`: OpenAI model to use (default: `gpt-4o-mini`)
- `gemini_model`: Gemini model to use (default: `gemini-2.0-flash-exp`)
- `repos` (or `repositories`): List of repositories to analyze
  - `name`: Repository identifier
  - `path`: Local path to the Git repository (for local repos)
  - `repo`: Remote repository URL (for remote repos, e.g., https://github.com/user/repo.git)
  - `author_email`: (Optional) Filter commits by this author email

**Note:** Each repository must specify either `path` (for local) or `repo` (for remote), but not both.

## CLI Commands

### `git-reporter init`

Initialize a new configuration file.

Options:
- `--config`, `-c`: Custom configuration file path

### `git-reporter add-repo`

Add a repository to the configuration.

Options:
- `--name`, `-n`: Repository name (required)
- `--path`, `-p`: Local path to repository (use this OR --repo)
- `--repo`, `-r`: Remote repository URL (use this OR --path)
- `--email`, `-e`: Filter commits by author email (optional)
- `--config`, `-c`: Custom configuration file path

**Note:** You must specify either `--path` or `--repo`, but not both.

### `git-reporter list-repos`

List all configured repositories.

Options:
- `--config`, `-c`: Custom configuration file path

### `git-reporter generate`

Generate a report from Git commit history.

Options:
- `--period`, `-p`: Report period (`daily`, `weekly`, `monthly`, `quarterly`, `yearly`, `custom`)
- `--start`, `-s`: Start date for custom period (YYYY-MM-DD)
- `--end`, `-e`: End date for custom period (YYYY-MM-DD)
- `--repo`, `-r`: Specific repositories to include (can be used multiple times)
- `--output`, `-o`: Output file path
- `--provider`: AI provider to use (overrides config)
- `--config`, `-c`: Custom configuration file path

## Examples

### Generate a Weekly Report

```bash
git-reporter generate --period weekly
```

### Generate a Monthly Report for Specific Repositories

```bash
git-reporter generate --period monthly --repo my-project --repo another-project
```

### Generate a Custom Period Report and Save to File

```bash
git-reporter generate --period custom --start 2024-01-01 --end 2024-03-31 --output Q1-2024-report.md
```

### Use Different AI Provider

```bash
git-reporter generate --period weekly --provider gemini
```

## AI Providers

### OpenAI

Supports models like:
- `gpt-4o` (most capable)
- `gpt-4o-mini` (faster and cheaper, default)
- `gpt-4-turbo`
- `gpt-3.5-turbo`

Get your API key from [OpenAI Platform](https://platform.openai.com/).

### Google Gemini

Supports models like:
- `gemini-2.0-flash-exp` (fastest, default)
- `gemini-1.5-pro`
- `gemini-1.5-flash`

Get your API key from [Google AI Studio](https://aistudio.google.com/).

## Development

See the [Contributing Guide](https://shenxianpeng.github.io/git-reporter/development/contributing/) for details on setting up a development environment and the [Project Structure](https://shenxianpeng.github.io/git-reporter/development/project-structure/) documentation for codebase overview.

## Contributing

Contributions are welcome! Please see our [Contributing Guide](https://shenxianpeng.github.io/git-reporter/development/contributing/) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [UV](https://github.com/astral-sh/uv) for fast dependency management
- Powered by [Pydantic-AI](https://github.com/pydantic/pydantic-ai) for AI model abstraction
- Uses [GitPython](https://github.com/gitpython-developers/GitPython) for Git operations
- Beautiful CLI with [Rich](https://github.com/Textualize/rich)

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/shenxianpeng/git-reporter/issues) on GitHub.

## Roadmap

- [ ] Add support for more AI providers (Anthropic Claude, etc.)
- [ ] Add web interface
- [ ] Support for team reports (multiple authors)
- [ ] Integration with project management tools (Jira, GitHub Issues)
- [ ] Custom report templates
- [ ] Report comparison and trends over time
- [ ] Email report delivery
- [ ] Docker container support
