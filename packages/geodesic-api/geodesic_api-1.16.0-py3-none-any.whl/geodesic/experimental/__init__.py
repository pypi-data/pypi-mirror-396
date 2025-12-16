"""Geodesic Experimental Features.

This module provides access to experimental features within the Geodesic
framework. These features are not yet stable and may change in future releases.
Use them with caution and be aware that the API may evolve.
"""

from typing import Any, Dict
from geodesic.experimental.registry import _registry
from geodesic.experimental.base import Extension

from geodesic.experimental.ontology import (
    OntologyExtension,
    SKOSTriple,
    Mapping,
    apply_mapping,
    get_mapping,
    list_mappings,
    get_linkml,
    write_linkml,
    add_ontology,
)

_registry.register(OntologyExtension)


class ExperimentalExtensions:
    """Namespace for accessing experimental extensions."""

    def __init__(self):
        self._registry = _registry

    def __getattr__(self, name: str) -> Extension:
        """Access extensions by attribute."""
        ext = self._registry.get(name)
        if ext is None:
            raise AttributeError(f"Extension '{name}' not found")
        return ext

    def list(self) -> Dict[str, Dict[str, Any]]:
        """List all available extensions."""
        return self._registry.list_all()


extensions = ExperimentalExtensions()

__all__ = [
    "extensions",
    "SKOSTriple",
    "Mapping",
    "apply_mapping",
    "get_mapping",
    "list_mappings",
    "get_linkml",
    "write_linkml",
    "add_ontology",
]
