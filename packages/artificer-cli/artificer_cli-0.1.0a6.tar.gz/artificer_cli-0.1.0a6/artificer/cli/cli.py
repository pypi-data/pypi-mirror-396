from __future__ import annotations

import click

from artificer.cli.config import ArtificerConfig, load_config
from artificer.cli.loader import import_feature


def build_cli(config: ArtificerConfig | None = None) -> click.Group:
    """Build the Artificer CLI with all registered features.

    Args:
        config: Optional configuration. If not provided, loads from pyproject.toml.

    Returns:
        Configured Click command group.
    """
    if config is None:
        config = load_config()

    @click.group()
    @click.version_option(package_name="artificer-cli")
    def cli() -> None:
        """Artificer Command Line Interface."""
        pass

    # Register features (in order)
    for feature_path in config.features:
        try:
            feature_class = import_feature(feature_path)
            feature_class.register(cli, config)
        except RuntimeError as e:
            # Re-raise with context about which feature failed
            raise RuntimeError(f"Failed to load feature '{feature_path}': {e}") from e

    return cli


def main() -> None:
    cli = build_cli()
    cli()


if __name__ == "__main__":
    main()
