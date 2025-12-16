from typing import Dict, Type, Optional, Any
from geodesic.experimental.base import Extension


class ExtensionRegistry:
    """Registry for managing experimental extensions."""

    def __init__(self):
        self._extensions: Dict[str, Extension] = {}

    def register(self, extension_class: Type[Extension]) -> None:
        """Register an extension class."""
        instance = extension_class()
        if instance.name in self._extensions:
            raise ValueError(f"Extension '{instance.name}' already registered")
        self._extensions[instance.name] = instance

    def get(self, name: str) -> Optional[Extension]:
        """Get an extension by name."""
        return self._extensions.get(name)

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """List all registered extensions with their status."""
        return {
            name: {
                "description": ext.description,
                "enabled": ext.is_enabled(),
                "dependencies": ext.dependencies,
            }
            for name, ext in self._extensions.items()
        }

    def enable_with_dependencies(self, name: str) -> None:
        """Enable extension and all its dependencies."""
        ext = self.get(name)
        if not ext:
            raise ValueError(f"Extension '{name}' not found")

        # Enable dependencies first
        for dep in ext.dependencies:
            dep_ext = self.get(dep)
            if not dep_ext:
                raise ValueError(f"Dependency '{dep}' not found")
            if not dep_ext.is_enabled():
                dep_ext.enable()

        # Enable the extension
        ext.enable()


# Global registry instance
_registry = ExtensionRegistry()

__all__ = ["_registry"]
