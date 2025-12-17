"""The adalib base module exposes the core integrations of all the components in the AdaLab platform."""

import importlib.metadata

_DISTRIBUTION_METADATA = importlib.metadata.metadata("adalib")
__project__ = _DISTRIBUTION_METADATA["name"]
__version__ = _DISTRIBUTION_METADATA["version"]
__description__ = _DISTRIBUTION_METADATA["description"]

__all__ = [
    "adaboard",
    "apps",
    "cards",
    "harbor",
    "issues",
    "keywords",
    "lab",
    "pictures",
    "schedules",
    "superset",
    "volumes",
]
