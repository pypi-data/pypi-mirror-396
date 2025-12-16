"""Genome CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer  # type: ignore[import]

from ..output import print_full_table, print_json, print_tsv
from ..utils import comma_join, ensure_client, handle_raw_response, merge_params, print_paginated_result

genomes_app = typer.Typer(help="Genome endpoints")


@genomes_app.command("list")
def list_genomes_command(
    ctx: typer.Context,
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    sort_field: Optional[str] = typer.Option(None, "--sort-field"),
    sort_order: Optional[str] = typer.Option(None, "--sort-order"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="json|tsv"),
) -> None:
    client = ensure_client(ctx)
    result = client.list_genomes(
        format=format or "json",
        page=page,
        per_page=per_page,
        sortField=sort_field,
        sortOrder=sort_order,
    )
    print_paginated_result(result, format, title="Genomes")


@genomes_app.command("search")
def search_genomes(
    ctx: typer.Context,
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Search term"),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    page: int = typer.Option(1, "--page", "-p"),
    per_page: int = typer.Option(10, "--per-page"),
    sort_field: Optional[str] = typer.Option(None, "--sort-field"),
    sort_order: Optional[str] = typer.Option(None, "--sort-order"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json|tsv (default: table)"),
) -> None:
    client = ensure_client(ctx)
    api_format = format or "json"  # Default to JSON for API request
    result = client.search_genomes(
        format=api_format,
        query=query,
        page=page,
        per_page=per_page,
        sort_field=sort_field,
        sort_order=sort_order,
        species_acronym=species_acronym,
    )
    
    if format == "tsv":
        print_tsv(result.items)
    elif format == "json":
        print_json(result.raw)
    else:
        # No format specified - display as table
        print_full_table(result.items, title="Genomes")


@genomes_app.command("type-strains")
def genomes_type_strains(
    ctx: typer.Context,
    format: Optional[str] = typer.Option(None, "--format", "-f", help="json|tsv"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", "/api/genomes/type-strains", format=format)
    handle_raw_response(response, format, title="Type Strains")


@genomes_app.command("autocomplete")
def genomes_autocomplete(
    ctx: typer.Context,
    query: str = typer.Option(..., "--query", "-q", help="Search term"),
    limit: Optional[int] = typer.Option(5, "--limit"),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="json|tsv"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "query": query,
            "limit": limit,
            "species_acronym": species_acronym,
        }
    )
    response = client.raw_request("GET", "/api/genomes/autocomplete", params=params, format=format)
    handle_raw_response(response, format, title="Genome Autocomplete")


@genomes_app.command("download")
def genomes_download_tsv(
    ctx: typer.Context,
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Destination file (defaults to stdout)"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", "/api/genomes/download/tsv", format="tsv")
    content = response.text
    if output:
        output.write_text(content)
        typer.echo(f"Wrote {output}")
    else:
        typer.echo(content)


@genomes_app.command("by-isolates")
def genomes_by_isolates(
    ctx: typer.Context,
    isolate: List[str] = typer.Option(..., "--isolate", "-i", help="Isolate name(s)"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="json|tsv"),
) -> None:
    client = ensure_client(ctx)
    params = {"isolates": comma_join(isolate)}
    response = client.raw_request("GET", "/api/genomes/by-isolate-names", params=params, format=format)
    handle_raw_response(response, format, title="Genomes by isolate")


@genomes_app.command("genes")
def genomes_genes(
    ctx: typer.Context,
    isolate_name: str = typer.Argument(..., help="Genome isolate name"),
    filter: Optional[str] = typer.Option(None, "--filter", help="Filter expression"),
    filter_operators: Optional[str] = typer.Option(None, "--filter-operators"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    sort_field: Optional[str] = typer.Option(None, "--sort-field"),
    sort_order: Optional[str] = typer.Option(None, "--sort-order"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "filter": filter,
            "filter_operators": filter_operators,
            "page": page,
            "per_page": per_page,
            "sort_field": sort_field,
            "sort_order": sort_order,
        }
    )
    response = client.raw_request(
        "GET",
        f"/api/genomes/{isolate_name}/genes",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"Genes for {isolate_name}")


@genomes_app.command("essentiality")
def genomes_essentiality(
    ctx: typer.Context,
    isolate_name: str = typer.Argument(..., help="Genome isolate name"),
    ref_name: str = typer.Argument(..., help="Reference/contig name"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request(
        "GET",
        f"/api/genomes/{isolate_name}/essentiality/{ref_name}",
        format=format,
    )
    handle_raw_response(response, format, title=f"Essentiality {isolate_name}:{ref_name}")


@genomes_app.command("drug-mic")
def genomes_drug_mic(
    ctx: typer.Context,
    isolate_name: str = typer.Argument(...),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params({"page": page, "per_page": per_page})
    response = client.raw_request(
        "GET",
        f"/api/genomes/{isolate_name}/drug-mic",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"Drug MIC ({isolate_name})")


@genomes_app.command("drug-metabolism")
def genomes_drug_metabolism(
    ctx: typer.Context,
    isolate_name: str = typer.Argument(...),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params({"page": page, "per_page": per_page})
    response = client.raw_request(
        "GET",
        f"/api/genomes/{isolate_name}/drug-metabolism",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"Drug metabolism ({isolate_name})")


@genomes_app.command("drug-data")
def genomes_drug_data(
    ctx: typer.Context,
    isolate_name: str = typer.Argument(...),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request(
        "GET",
        f"/api/genomes/{isolate_name}/drug-data",
        format=format,
    )
    handle_raw_response(response, format, title=f"Drug data ({isolate_name})")

