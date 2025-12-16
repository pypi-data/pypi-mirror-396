"""Geodesic Experimental Features for Ontology Management.

This module provides experimental features for ontology management
within the Geodesic framework, including classes and functions for handling
ontologies and mappings.
"""

import geodesic
from geodesic.experimental.base import Extension
from geodesic.config import SearchReturnType
from geodesic.experimental.ontology.mappings import (
    SKOSTriple,
    Mapping,
    apply_mapping,
    get_mapping,
    list_mappings,
)

from geodesic.experimental.ontology.ontology import add_ontology
from geodesic.experimental.ontology.search import search_decorator
from geodesic.experimental.ontology.linkml import get_linkml, write_linkml


class OntologyExtension(Extension):
    """Experimental extension for ontology management in Geodesic."""

    name = "ontology"
    description = "Provides ontology mapping on geodesic Datasets"
    dependencies = []

    def _apply_patches(self) -> None:
        """Apply ontology patches to geodesic.Dataset."""
        # Store originals
        search = getattr(geodesic.Dataset, "search", None)
        self._patches["search"] = search
        self._patches["apply_mapping"] = getattr(geodesic.Dataset, "apply_mapping", None)
        self._patches["get_mapping"] = getattr(geodesic.Dataset, "get_mapping", None)
        self._patches["list_mappings"] = getattr(geodesic.Dataset, "list_mappings", None)
        self._patches["add_ontology"] = getattr(geodesic.Dataset, "add_ontology", None)
        self._patches["get_linkml"] = getattr(geodesic.Dataset, "get_linkml", None)
        self._patches["write_linkml"] = getattr(geodesic.Dataset, "write_linkml", None)

        new_search = search_decorator(search)
        setattr(geodesic.Dataset, "search", new_search)

        # Apply patches/additions
        geodesic.Dataset.apply_mapping = apply_mapping
        geodesic.Dataset.get_mapping = get_mapping
        geodesic.Dataset.list_mappings = list_mappings
        geodesic.Dataset.add_ontology = add_ontology
        geodesic.Dataset.get_linkml = get_linkml
        geodesic.Dataset.write_linkml = write_linkml

        _SearchReturnType = SearchReturnType
        setattr(_SearchReturnType, "RDFLIB_GRAPH", 3)
        setattr(geodesic, "SearchReturnType", _SearchReturnType)
        setattr(geodesic.config, "SearchReturnType", _SearchReturnType)

    def _remove_patches(self):
        """Remove ontology patches from geodesic.Dataset."""
        # Restore or delete
        for attr_name, original in self._patches.items():
            if original is None:
                delattr(geodesic.Dataset, attr_name)
            else:
                setattr(geodesic.Dataset, attr_name, original)
        setattr(geodesic.config, "SearchReturnType", SearchReturnType)
        setattr(geodesic, "SearchReturnType", SearchReturnType)

        self._patches.clear()


__all__ = [
    "OntologyExtension",
    "SKOSTriple",
    "Mapping",
    "apply_mapping",
    "get_mapping",
    "list_mappings",
    "get_linkml",
    "write_linkml",
    "add_ontology",
]
