"""ArtificerFeature base class."""

from __future__ import annotations

import click

from artificer.cli.config import ArtificerConfig


class ArtificerFeature:
    """Base class for Artificer features.

    Features extend the CLI by registering commands and initializing subsystems.
    All functionality should be contained within the register() method.
    """

    @classmethod
    def register(cls, cli: click.Group, config: ArtificerConfig) -> None:
        """Register this feature with the CLI.

        Args:
            cli: The root Click command group to extend.
            config: The Artificer configuration.

        Raises:
            NotImplementedError: Subclasses must implement this method.
        """
        raise NotImplementedError(
            f"{cls.__name__} must implement the register() method."
        )
