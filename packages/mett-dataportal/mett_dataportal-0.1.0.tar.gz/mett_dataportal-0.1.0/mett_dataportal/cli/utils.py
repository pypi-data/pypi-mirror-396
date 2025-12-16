"""Shared utility functions for CLI commands."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import typer  # type: ignore[import]

from ..client import DataPortalClient
from ..config import get_config
from .output import print_full_table, print_json, print_tsv


def _build_client(
    *,
    base_url: Optional[str],
    jwt: Optional[str],
    timeout: Optional[int],
    verify_ssl: Optional[bool],
) -> DataPortalClient:
    """Build a DataPortalClient with the given configuration."""
    config = get_config()
    if base_url:
        config.base_url = base_url.rstrip("/")
    if jwt:
        config.jwt_token = jwt
    if timeout is not None:
        config.timeout = timeout
    if verify_ssl is not None:
        config.verify_ssl = verify_ssl
    return DataPortalClient(config=config)


def ensure_client(ctx: typer.Context) -> DataPortalClient:
    """Get or create a client from the Typer context."""
    if ctx.obj is None:
        ctx.obj = DataPortalClient(config=get_config())
    return ctx.obj


def parse_key_value_pairs(
    pairs: Optional[Sequence[str]],
    *,
    separator: str = "=",
    error_message: str = "Expected KEY=VALUE",
) -> Dict[str, str]:
    """Parse a sequence of KEY=VALUE strings into a dictionary."""
    parsed: Dict[str, str] = {}
    if not pairs:
        return parsed
    for pair in pairs:
        if separator not in pair:
            raise typer.BadParameter(error_message)
        key, value = pair.split(separator, 1)
        parsed[key.strip()] = value.strip()
    return parsed


def merge_params(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries, skipping None values."""
    merged: Dict[str, Any] = {}
    for mapping in dicts:
        for key, value in mapping.items():
            if value is None:
                continue
            merged[key] = value
    return merged


def extract_table_rows(payload: Any) -> Optional[List[Any]]:
    """Extract table rows from a JSON payload."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "results", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return None


def handle_raw_response(response: Any, format: Optional[str], *, title: str) -> None:
    """Handle a raw HTTP response and format it appropriately."""
    content_type = (response.headers.get("Content-Type") or "").lower()
    if (format or "").lower() == "tsv":
        # If TSV format requested, check if response is already TSV
        if "text/tab-separated" in content_type:
            typer.echo(response.text)
            return

        # Otherwise, parse JSON and convert to TSV
        try:
            payload = response.json()
        except ValueError:
            # If not JSON, just output as-is
            typer.echo(response.text)
            return

        # Extract rows from JSON payload
        rows = extract_table_rows(payload)
        if rows:
            print_tsv(rows)
        else:
            # If we can't extract rows, output as JSON (fallback)
            print_json(payload)
        return

    try:
        payload = response.json()
    except ValueError:
        typer.echo(response.text)
        return

    if (format or "").lower() == "json":
        print_json(payload)
        return

    rows = extract_table_rows(payload)
    if rows:
        print_full_table(rows, title=title)
    else:
        print_json(payload)


def comma_join(values: Optional[Sequence[str]]) -> Optional[str]:
    """Join a sequence of strings with commas."""
    if not values:
        return None
    return ",".join(values)


def print_paginated_result(result: Any, format: Optional[str], *, title: str) -> None:
    """Print a paginated result in the requested format."""
    if format == "tsv":
        print_tsv(result.items)
        return
    if format == "json":
        print_json(result.raw)
        return
    print_full_table(result.items, title=title)

