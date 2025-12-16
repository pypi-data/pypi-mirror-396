"""Operons CLI commands."""

from __future__ import annotations

from typing import Optional

import typer  # type: ignore[import]

from ..utils import ensure_client, handle_raw_response, merge_params

operons_app = typer.Typer(help="Operon endpoints")


@operons_app.command("search")
def operons_search(
    ctx: typer.Context,
    locus_tag: Optional[str] = typer.Option(None, "--locus-tag"),
    operon_id: Optional[str] = typer.Option(None, "--operon-id"),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    isolate_name: Optional[str] = typer.Option(None, "--isolate"),
    has_tss: Optional[bool] = typer.Option(None, "--has-tss"),
    has_terminator: Optional[bool] = typer.Option(None, "--has-terminator"),
    min_gene_count: Optional[int] = typer.Option(None, "--min-genes"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "locus_tag": locus_tag,
            "operon_id": operon_id,
            "species_acronym": species_acronym,
            "isolate_name": isolate_name,
            "has_tss": has_tss,
            "has_terminator": has_terminator,
            "min_gene_count": min_gene_count,
            "page": page,
            "per_page": per_page,
        }
    )
    response = client.raw_request("GET", "/api/operons/search", params=params, format=format)
    handle_raw_response(response, format, title="Operon search")


@operons_app.command("get")
def operons_get(
    ctx: typer.Context,
    operon_id: str = typer.Argument(...),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", f"/api/operons/{operon_id}", format=format)
    handle_raw_response(response, format, title=f"Operon {operon_id}")


@operons_app.command("statistics")
def operons_statistics(
    ctx: typer.Context,
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params({"species_acronym": species_acronym})
    response = client.raw_request("GET", "/api/operons/statistics", params=params, format=format)
    handle_raw_response(response, format, title="Operon statistics")

