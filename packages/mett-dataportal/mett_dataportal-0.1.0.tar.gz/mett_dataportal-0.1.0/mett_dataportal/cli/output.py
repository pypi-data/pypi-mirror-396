"""CLI output helpers using Rich."""

from __future__ import annotations

import csv
import json
import sys
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from rich.console import Console  # type: ignore[import]
from rich.table import Table  # type: ignore[import]

console = Console()

Column = Tuple[str, callable]


def print_table(rows: Iterable[object], columns: Sequence[Column], *, title: str) -> None:
    rows = list(rows)
    if not rows:
        console.print("No results found", style="yellow")
        return
    table = Table(title=title)
    for header, _ in columns:
        table.add_column(header)

    for row in rows:
        table.add_row(*[str(getter(row) or "") for _, getter in columns])
    console.print(table)


def print_full_table(rows: Iterable[object], *, title: str) -> None:
    normalized = [_normalize_row(row) for row in rows]
    if not normalized:
        console.print("No results found", style="yellow")
        return

    headers: List[str] = sorted({key for row in normalized for key in row.keys()})
    table = Table(title=title)
    for header in headers:
        table.add_column(header)

    for row in normalized:
        table.add_row(*[_stringify(row.get(header)) for header in headers])
    console.print(table)


def print_json(data: object) -> None:
    console.print_json(data=json.loads(json.dumps(data, default=str)))


def print_tsv(rows: Iterable[object]) -> None:
    """Print rows as raw TSV (tab-separated values) for piping to files."""
    normalized = [_normalize_row(row) for row in rows]
    if not normalized:
        return

    headers: List[str] = sorted({key for row in normalized for key in row.keys()})
    
    # Use csv.writer with tab delimiter for proper TSV formatting
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(headers)
    
    for row in normalized:
        values = [_tsv_value(row.get(header)) for header in headers]
        writer.writerow(values)


def _normalize_row(row: object) -> Dict[str, Any]:
    if isinstance(row, Mapping):
        return dict(row)
    if hasattr(row, "model_dump"):
        return row.model_dump()
    if hasattr(row, "__dict__"):
        return {k: v for k, v in vars(row).items() if not k.startswith("_")}
    return {"value": row}


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:  # pragma: no cover
            return str(value)
    return str(value)


def _tsv_value(value: Any) -> str:
    """Convert value to TSV-safe string."""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:  # pragma: no cover
            return str(value)
    return str(value)
