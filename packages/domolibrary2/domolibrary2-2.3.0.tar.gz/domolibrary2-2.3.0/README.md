> Last updated: 2025-11-17

# Domolibrary

A Python library for interacting with Domo APIs.

> This project includes **GitHub Copilot custom prompts** for enhanced development workflows. See the [Copilot Kit section](#github-copilot-integration) below.

## Installation

```bash
pip install domolibrary
```

## Usage

```python
from domolibrary import DomoUser
# Your code here
```

## Project Structure

```
src/                      # Main package source code
├── classes/              # Domain model classes
├── client/               # API client utilities
├── integrations/         # Integration modules
├── routes/               # API route implementations
├── utils/                # Utility functions
├── __init__.py           # Package initialization
└── _modidx.py           # Module index
scripts/                  # Development scripts
tests/                    # Test files
.vscode/                  # VS Code configuration
.github/workflows/        # CI/CD workflows
```

## Development

This project uses `uv` for dependency management and development.

### Setup Development Environment

```powershell
# Initial setup (run once)
.\scripts\setup-dev.ps1
```

This will:
- Install all dependencies (including dev dependencies)
- Set up pre-commit hooks for automatic code quality checks

### Development Scripts

All development scripts are located in the `scripts/` folder. See `scripts/README.md` for detailed documentation.

**Quick reference:**
- **`.\scripts\setup-dev.ps1`** - Setup development environment
- **`.\scripts\format-code.ps1`** - Manual code formatting (fallback)
- **`.\scripts\lint.ps1`** - Run linting and type checking
- **`.\scripts\test.ps1`** - Run tests with coverage
- **`.\scripts\build.ps1`** - Build the package
- **`.\scripts\publish.ps1`** - Publish to PyPI (with validation)

### Manual Development Commands

If you prefer to run commands manually:

```powershell
# Install dependencies
uv sync --dev

# Run linting
uv run ruff check src --fix
uv run black src
uv run isort src
uv run pylint src
uv run mypy src

# Run tests
uv run pytest tests/ --cov=src

# Build package
uv build

# Publish (after all checks pass)
uv publish
```

### Pre-commit Hooks

This project uses pre-commit hooks to automatically check code quality before commits:
- **Ruff** - Fast Python linter
- **Black** - Code formatter
- **isort** - Import sorter

Hooks are installed automatically by `setup-dev.ps1`. If they cause issues, you can use `.\scripts\format-code.ps1` as a fallback.

## GitHub Copilot Integration

This project includes a curated collection of GitHub Copilot custom prompts and MCP (Model Context Protocol) server configurations to enhance your development workflow.

### 🎨 Custom Prompts

Ready-to-use prompts for common development tasks:

| Prompt | Description | Usage |
|--------|-------------|-------|
| [architecture-review](.github/prompts/architecture-review.prompt.md) | Focused architectural review with actionable feedback | `/architecture-review` |
| [code-review](.github/prompts/code-review.prompt.md) | High-rigor, tech-agnostic code review | `/code-review` |
| [pragmatic-code-review](.github/prompts/pragmatic-code-review.prompt.md) | Production-focused code review balancing rigor with constraints | `/pragmatic-code-review` |
| [refactor](.github/prompts/refactor.prompt.md) | Intelligent refactoring with best practices | `/refactor` |
| [optimize-performance](.github/prompts/optimize-performance.prompt.md) | Identify and fix performance anti-patterns | `/optimize-performance` |
| [document](.github/prompts/document.prompt.md) | Generate exceptional documentation with diagrams | `/document` |
| [create-prompt](.github/prompts/create-prompt.prompt.md) | Meta-prompt to generate new custom prompts | `/create-prompt` |

### 🤖 MCP Server Configuration

Model Context Protocol (MCP) lets Copilot connect to external tool servers for enhanced capabilities:

- **Sequential Thinking** - Structured thinking process for complex tasks
- **Memory** - Remember context between conversations
- **Context7** - Access to up-to-date framework documentation
- **Shadcn UI** - Shadcn UI component knowledge (if using React)
- **Chrome DevTools** - Browser debugging capabilities

#### Quick MCP Setup

1. **Copy memory template**:
   ```bash
   cp .mcp/memory.json.dist .mcp/memory.json
   ```
   ⚠️ Never commit `.mcp/memory.json` - add to `.gitignore`

2. **Configure servers**: The `.vscode/mcp.json` file is already set up with recommended servers. Copilot will prompt for any required API keys on first use.

3. **Enable MCP in VS Code**: Ensure GitHub Copilot Chat has MCP enabled in settings.

### 📚 Documentation

- **[Custom Prompts Guide](docs/copilot-kit/custom-prompts-guide.md)** - Comprehensive guide on using and creating prompts
- **[Testing Guide](docs/copilot-kit/testing-guide.md)** - How to verify your setup is working correctly
- **[Fork Sync Guide](docs/copilot-kit/fork-sync-guide.md)** - Information about keeping copilot-kit files updated

### Using Prompts

Invoke prompts in GitHub Copilot Chat using the slash command:

```text
/code-review
/refactor
/document
```

With optional arguments:
```text
/code-review focus=security
/pragmatic-code-review maintainability
/optimize-performance
```

See the [Custom Prompts Guide](docs/copilot-kit/custom-prompts-guide.md) for detailed usage instructions.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project, including information about custom prompts and code review standards.
