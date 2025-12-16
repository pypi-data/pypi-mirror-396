"""Version information for the METT Data Portal client."""

from __future__ import annotations

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8
    from importlib_metadata import version, PackageNotFoundError  # type: ignore[no-redef]

try:
    __version__ = version("mett-dataportal")
except PackageNotFoundError:
    # Package is not installed, read from pyproject.toml
    from pathlib import Path
    
    try:
        # Try tomllib (Python 3.11+)
        try:
            import tomllib
        except ImportError:
            # Fall back to tomli for Python < 3.11
            import tomli as tomllib  # type: ignore[no-redef]
        
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject = tomllib.load(f)
        __version__ = pyproject["project"]["version"]
    except (FileNotFoundError, KeyError, ImportError):
        # Fallback if pyproject.toml is not found or can't be parsed
        __version__ = "0.1.0"

__all__ = ["__version__"]

