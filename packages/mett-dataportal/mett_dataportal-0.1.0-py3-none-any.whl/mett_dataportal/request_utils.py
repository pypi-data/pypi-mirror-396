"""Request/Responseutilities for the METT Data Portal client."""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, List, Optional

import requests  # type: ignore[import]

from .config import Config
from .exceptions import APIError, AuthenticationError


def parse_tsv_response(tsv_text: str) -> List[Dict[str, Any]]:
    """Parse TSV response into a list of dictionaries.
    
    Assumes first row contains headers. Returns list of dicts where keys are header names.
    """
    if not tsv_text.strip():
        return []
    
    reader = csv.DictReader(io.StringIO(tsv_text), delimiter="\t")
    return [dict(row) for row in reader]


def request_json(
    session: requests.Session,
    config: Config,
    endpoint: str,
    *,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    """Direct HTTP GET for endpoints that don't match the published schema.
    
    Supports both JSON (default) and TSV (format=tsv) responses.
    """
    url = f"{config.base_url.rstrip('/')}{endpoint}"
    format_type = (params or {}).get("format", "json")
    
    # Prepare headers based on format
    headers = {}
    if format_type == "tsv":
        headers["Accept"] = "text/tab-separated-values"
    else:
        headers["Accept"] = "application/json"
    
    try:
        resp = session.get(
            url,
            params=params,
            headers=headers,
            timeout=config.timeout,
            verify=config.verify_ssl,
        )
        resp.raise_for_status()
        
        # Parse TSV if requested
        if format_type == "tsv":
            return parse_tsv_response(resp.text)
        
        # Default: parse JSON
        return resp.json()
    except requests.exceptions.HTTPError as exc:
        if exc.response is not None and exc.response.status_code in {401, 403}:
            raise AuthenticationError("Authentication failed", status_code=exc.response.status_code) from exc
        status = exc.response.status_code if exc.response is not None else None
        raise APIError(f"Request failed: {exc}", status_code=status) from exc
    except requests.exceptions.RequestException as exc:
        raise APIError(f"Request failed: {exc}") from exc
    except (ValueError, csv.Error) as exc:
        raise APIError(f"Failed to parse TSV response: {exc}") from exc


__all__ = ["parse_tsv_response", "request_json"]

