from abc import ABC, abstractmethod
from typing import Any, Dict, List
import warnings


class Extension(ABC):
    """Abstract base class for geodesic extensions."""

    name: str = ""
    description: str = ""
    dependencies: List[str] = []

    def __init__(self):
        self._patches: Dict[str, Any] = {}
        self._is_enabled: bool = False

    @abstractmethod
    def _apply_patches(self) -> None:
        """Apply the monkey patches. Store originals in self._patches."""
        pass

    @abstractmethod
    def _remove_patches(self) -> None:
        """Remove the monkey patches, restoring originals from self._patches."""

    def enable(self) -> None:
        """Enable the extension by applying patches."""
        if self._is_enabled:
            warnings.warn(f"Extension '{self.name}' is already enabled.", UserWarning)
            return

        self._apply_patches()
        self._is_enabled = True
        warnings.warn(
            f"Experimental feature '{self.name}' has been enabled. "
            "This API is not stable and may change.",
            FutureWarning,
        )

    def disable(self) -> None:
        """Disable the extension by removing patches."""
        if not self._is_enabled:
            return

        self._remove_patches()
        self._is_enabled = False

    def is_enabled(self) -> bool:
        """Check if the extension is enabled."""
        return self._is_enabled

    def __enter__(self):
        """Enable the extension in a context manager."""
        self.enable()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Disable the extension when exiting a context manager."""
        self.disable()
