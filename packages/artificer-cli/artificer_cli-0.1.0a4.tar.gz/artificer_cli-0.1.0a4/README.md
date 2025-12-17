# artificer-cli

The shared CLI interface for the [Artificer](https://github.com/artificer-ai) project — AI dev tooling built on MCP (Model Context Protocol).

## What is this?

A minimal, configuration-driven CLI that dynamically loads features from installed Artificer packages. Instead of shipping a monolithic CLI, each Artificer package (workflows, conversations, etc.) registers its own commands through a simple plugin system.

## Installation

```bash
pip install artificer-cli
```

## Usage

```bash
artificer --help
artificer --version
```

Commands are added by installing Artificer feature packages and registering them in your `pyproject.toml`:

```toml
[tool.artificer]
features = [
    "artificer.workflows.feature.WorkflowFeature",
    "artificer.conversations.feature.ConversationFeature"
]
```

## Creating Features

Features extend `ArtificerFeature` and implement `register()`:

```python
from artificer.cli.feature import ArtificerFeature
from artificer.cli.config import ArtificerConfig
import click

class MyFeature(ArtificerFeature):
    @classmethod
    def register(cls, cli: click.Group, config: ArtificerConfig) -> None:
        @cli.command()
        def my_command():
            """Does something useful."""
            click.echo("Hello from my feature")
```

## Architecture

- **config.py** — Loads `[tool.artificer]` from pyproject.toml
- **feature.py** — Base class for all features
- **loader.py** — Dynamic feature import and validation
- **cli.py** — Builds the Click CLI from config

The `artificer/` directory is a PEP 420 namespace package, allowing other packages to extend it (e.g., `artificer.workflows`, `artificer.mcp`).

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
./scripts/test.sh

# Type check
./scripts/typecheck.sh

# All checks
./scripts/check.sh
```

## License

MIT
