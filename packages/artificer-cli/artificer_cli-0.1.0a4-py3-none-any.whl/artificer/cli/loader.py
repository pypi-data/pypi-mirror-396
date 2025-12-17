"""Feature discovery and loading."""

from __future__ import annotations

import importlib

from artificer.cli.feature import ArtificerFeature


def import_feature(feature_path: str) -> type[ArtificerFeature]:
    """Import a feature by its full module path.

    Args:
        feature_path: Full dotted path to feature class
            (e.g., "artificer.workflows.feature.WorkflowFeature").

    Returns:
        The feature class.

    Raises:
        RuntimeError: If feature cannot be imported.
    """
    if "." not in feature_path:
        raise RuntimeError(
            f"Invalid feature path '{feature_path}'. "
            "Must be a full module path (e.g., 'mypackage.feature.MyFeature')."
        )

    module_name, class_name = feature_path.rsplit(".", 1)

    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise RuntimeError(
            f"Failed to import feature '{feature_path}': {e}. Is the package installed?"
        ) from e

    try:
        feature_class = getattr(module, class_name)
    except AttributeError as e:
        raise RuntimeError(
            f"Module '{module_name}' does not have class '{class_name}'."
        ) from e

    if not isinstance(feature_class, type) or not issubclass(
        feature_class, ArtificerFeature
    ):
        raise RuntimeError(f"'{feature_path}' is not a subclass of ArtificerFeature.")

    return feature_class
