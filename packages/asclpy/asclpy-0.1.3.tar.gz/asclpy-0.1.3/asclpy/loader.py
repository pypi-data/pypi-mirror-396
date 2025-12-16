"""
Tuning registry and loading logic for .ascl files.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from .parser import parse_ascl_file
from .tuning import Tuning
from .validation import validate_ascl_data


class TuningRegistry:
    """Registry for managing pre-loaded and custom tunings."""

    def __init__(self, tunings_dir: Optional[Path] = None, auto_load: bool = True):
        """
        Initialize tuning registry.

        Args:
            tunings_dir: Directory containing .ascl files. If None, uses bundled tunings.
            auto_load: If True, load all tunings from directory on initialization.
        """
        self._tunings: Dict[str, Tuning] = {}

        if tunings_dir is None:
            # Use bundled tunings directory
            tunings_dir = Path(__file__).parent / "tunings"

        self._tunings_dir = tunings_dir

        if auto_load and self._tunings_dir.exists():
            self._load_bundled_tunings()

    def _load_bundled_tunings(self) -> None:
        """Load all .ascl files from the tunings directory."""
        # Recursively find all .ascl files
        for ascl_file in self._tunings_dir.rglob("*.ascl"):
            # Skip the specification file
            if "Specification" in ascl_file.name:
                continue

            try:
                # Parse and validate the file
                data = parse_ascl_file(ascl_file)
                warnings_list = validate_ascl_data(data, strict=False)
                data.validation_warnings = warnings_list
                tuning = Tuning(data)

                # Generate snake_case key from filename
                key = self._to_snake_case(ascl_file.stem)

                # Handle potential duplicates by adding parent directory
                if key in self._tunings:
                    parent_name = self._to_snake_case(ascl_file.parent.name)
                    key = f"{parent_name}_{key}"

                self._tunings[key] = tuning

            except Exception as e:
                # Gracefully skip files that fail to parse
                import warnings

                warnings.warn(f"Failed to load tuning {ascl_file.name}: {e}")

    def load(self, name_or_path: str | Path) -> Tuning:
        """
        Load a tuning by name or from a file path.

        Args:
            name_or_path: Either a snake_case tuning name from the registry,
                         or a path to an .ascl file

        Returns:
            Tuning object

        Raises:
            KeyError: If tuning name is not found in registry
            ValueError: If file cannot be parsed

        Examples:
            >>> registry = TuningRegistry()
            >>> tuning = registry.load("12_tet_edo")
            >>> tuning = registry.load("/path/to/custom.ascl")
        """
        name_or_path = str(name_or_path)

        # Check if it's a known tuning name
        if name_or_path in self._tunings:
            return self._tunings[name_or_path]

        # Otherwise, try to load it as a file path
        path = Path(name_or_path)
        if path.exists():
            data = parse_ascl_file(path)
            warnings_list = validate_ascl_data(data, strict=False)
            data.validation_warnings = warnings_list
            return Tuning(data)

        # Not found
        available = ", ".join(sorted(self._tunings.keys())[:10])
        raise KeyError(
            f"Tuning '{name_or_path}' not found. Available tunings: {available}..."
        )

    def list(self) -> List[str]:
        """
        Get a list of all available tuning names.

        Returns:
            Sorted list of tuning names
        """
        return sorted(self._tunings.keys())

    def register(self, name: str, tuning: Tuning) -> None:
        """
        Register a custom tuning with a name.

        Args:
            name: Name to register the tuning under (will be converted to snake_case)
            tuning: Tuning object to register
        """
        key = self._to_snake_case(name)
        self._tunings[key] = tuning

    def unregister(self, name: str) -> None:
        """
        Remove a tuning from the registry.

        Args:
            name: Name of the tuning to remove

        Raises:
            KeyError: If tuning name is not found
        """
        if name in self._tunings:
            del self._tunings[name]
        else:
            raise KeyError(f"Tuning '{name}' not found in registry")

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """
        Convert a tuning name to snake_case.

        Examples:
            "12-TET (EDO)" -> "12_tet_edo"
            "Helmholtz temperament" -> "helmholtz_temperament"
            "Well Temperament (Kirnberger III)" -> "well_temperament_kirnberger_iii"
        """
        # Remove file extension
        name = name.replace(".ascl", "")

        # Replace spaces and special characters with underscores
        name = re.sub(r"[^\w\s-]", "", name)
        name = re.sub(r"[-\s]+", "_", name)

        # Convert to lowercase
        name = name.lower()

        # Remove multiple consecutive underscores
        name = re.sub(r"_+", "_", name)

        # Strip leading/trailing underscores
        name = name.strip("_")

        return name


# Global registry instance for convenience
_default_registry: Optional[TuningRegistry] = None


def get_default_registry() -> TuningRegistry:
    """
    Get the default tuning registry (lazy-loaded).

    Returns:
        Default TuningRegistry instance
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = TuningRegistry()
    return _default_registry


def load_tuning(name_or_path: str | Path) -> Tuning:
    """
    Load a tuning by name or from a file path using the default registry.

    Args:
        name_or_path: Either a snake_case tuning name or a path to an .ascl file

    Returns:
        Tuning object

    Examples:
        >>> tuning = load_tuning("12_tet_edo")
        >>> tuning = load_tuning("/path/to/custom.ascl")
    """
    return get_default_registry().load(name_or_path)


def list_tunings() -> List[str]:
    """
    Get a list of all available tuning names from the default registry.

    Returns:
        Sorted list of tuning names
    """
    return get_default_registry().list()
