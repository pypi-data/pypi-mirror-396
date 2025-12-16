"""Utility functions for the METT Data Portal client."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from .models import Species


def normalize_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize parameter keys to snake_case and filter None values."""
    normalized: Dict[str, Any] = {}
    for key, value in params.items():
        if value is None:
            continue
        if key.startswith("_"):
            normalized[key] = value
            continue
        if any(ch.isupper() for ch in key):
            snake = re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()
            normalized[snake] = value
        else:
            normalized[key] = value
    return normalized


def normalize_species_entry(entry: Any) -> Species:
    """Normalize a species entry from various API response formats."""
    if hasattr(entry, "model_dump"):
        entry = entry.model_dump()
    if not isinstance(entry, dict):
        return {
            "species_scientific_name": str(entry),
            "species_acronym": None,
            "description": None,
            "taxonomy_id": None,
        }

    def _first(*keys: str) -> Optional[Any]:
        for key in keys:
            if key in entry and entry[key] not in (None, ""):
                return entry[key]
        return None

    return {
        "species_acronym": _first("species_acronym", "acronym", "short_name"),
        "species_scientific_name": _first("species_scientific_name", "scientific_name", "name"),
        "description": _first("description", "common_name"),
        "taxonomy_id": _first("taxonomy_id", "tax_id"),
    }


__all__ = ["normalize_params", "normalize_species_entry"]

