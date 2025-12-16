"""Orthologs CLI commands."""

from __future__ import annotations

from typing import Optional

import typer  # type: ignore[import]

from ..utils import ensure_client, handle_raw_response, merge_params

orthologs_app = typer.Typer(help="Ortholog endpoints")


@orthologs_app.command("search")
def orthologs_search(
    ctx: typer.Context,
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    orthology_type: Optional[str] = typer.Option(None, "--orthology-type"),
    one_to_one_only: Optional[bool] = typer.Option(None, "--one-to-one-only"),
    cross_species_only: Optional[bool] = typer.Option(None, "--cross-species-only"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "species_acronym": species_acronym,
            "orthology_type": orthology_type,
            "one_to_one_only": one_to_one_only,
            "cross_species_only": cross_species_only,
            "page": page,
            "per_page": per_page,
        }
    )
    response = client.raw_request("GET", "/api/orthologs/search", params=params, format=format)
    handle_raw_response(response, format, title="Ortholog search")


@orthologs_app.command("pair")
def orthologs_pair(
    ctx: typer.Context,
    locus_tag_a: str = typer.Option(..., "--gene-a"),
    locus_tag_b: str = typer.Option(..., "--gene-b"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = {
        "locus_tag_a": locus_tag_a,
        "locus_tag_b": locus_tag_b,
    }
    response = client.raw_request("GET", "/api/orthologs/pair", params=params, format=format)
    handle_raw_response(response, format, title="Ortholog pair")

