"""Species CLI commands."""

from __future__ import annotations

from typing import List, Optional

import typer  # type: ignore[import]

from ..output import print_full_table, print_json, print_tsv
from ..utils import comma_join, ensure_client, handle_raw_response, merge_params

species_app = typer.Typer(help="Species endpoints")


@species_app.command("list")
def list_species(
    ctx: typer.Context,
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json|tsv (default: table)"),
) -> None:
    client = ensure_client(ctx)
    api_format = format or "json"  # Default to JSON for API request
    species = client.list_species(format=api_format)
    
    if format == "tsv":
        print_tsv(species)
    elif format == "json":
        print_json(species)
    else:
        # No format specified - display as table
        print_full_table(species, title="Species")


@species_app.command("genomes")
def species_genomes_list(
    ctx: typer.Context,
    species_acronym: str = typer.Argument(..., help="Species acronym, e.g. BU"),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Optional search term"),
    isolates: Optional[List[str]] = typer.Option(None, "--isolate", "-i", help="Filter by isolate(s)"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    sort_field: Optional[str] = typer.Option(None, "--sort-field"),
    sort_order: Optional[str] = typer.Option(None, "--sort-order"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="json|tsv"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "query": query,
            "page": page,
            "per_page": per_page,
            "sortField": sort_field,
            "sortOrder": sort_order,
            "isolates": comma_join(isolates),
        }
    )
    response = client.raw_request(
        "GET",
        f"/api/species/{species_acronym}/genomes",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"Genomes ({species_acronym})")


@species_app.command("search-genomes")
def species_search_genomes(
    ctx: typer.Context,
    species_acronym: str = typer.Argument(..., help="Species acronym, e.g. BU"),
    query: Optional[str] = typer.Option(None, "--query", "-q"),
    isolates: Optional[List[str]] = typer.Option(None, "--isolate", "-i"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    sort_field: Optional[str] = typer.Option(None, "--sort-field"),
    sort_order: Optional[str] = typer.Option(None, "--sort-order"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="json|tsv"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "query": query,
            "page": page,
            "per_page": per_page,
            "sortField": sort_field,
            "sortOrder": sort_order,
            "isolates": comma_join(isolates),
        }
    )
    response = client.raw_request(
        "GET",
        f"/api/species/{species_acronym}/genomes/search",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"Genomes search ({species_acronym})")

