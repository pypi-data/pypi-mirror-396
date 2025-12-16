"""Fitness CLI commands."""

from __future__ import annotations

from typing import List, Optional

import typer  # type: ignore[import]

from ..utils import comma_join, ensure_client, handle_raw_response, merge_params

fitness_app = typer.Typer(help="Fitness endpoints")
fitness_corr_app = typer.Typer(help="Fitness correlation endpoints")


@fitness_app.command("search")
def fitness_search(
    ctx: typer.Context,
    locus_tags: Optional[List[str]] = typer.Option(None, "--locus-tag"),
    uniprot_ids: Optional[List[str]] = typer.Option(None, "--uniprot"),
    contrast: Optional[str] = typer.Option(None, "--contrast"),
    min_lfc: Optional[float] = typer.Option(None, "--min-lfc"),
    max_fdr: Optional[float] = typer.Option(None, "--max-fdr"),
    min_barcodes: Optional[int] = typer.Option(None, "--min-barcodes"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "locus_tags": comma_join(locus_tags),
            "uniprot_ids": comma_join(uniprot_ids),
            "contrast": contrast,
            "min_lfc": min_lfc,
            "max_fdr": max_fdr,
            "min_barcodes": min_barcodes,
        }
    )
    response = client.raw_request("GET", "/api/fitness/search", params=params, format=format)
    handle_raw_response(response, format, title="Fitness search")


@fitness_corr_app.command("search")
def fitness_correlations_search(
    ctx: typer.Context,
    query: str = typer.Option(..., "--query", "-q"),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "query": query,
            "species_acronym": species_acronym,
            "page": page,
            "per_page": per_page,
        }
    )
    response = client.raw_request("GET", "/api/fitness-correlations/search", params=params, format=format)
    handle_raw_response(response, format, title="Fitness correlations search")


@fitness_corr_app.command("pair")
def fitness_correlations_pair(
    ctx: typer.Context,
    locus_tag_a: str = typer.Option(..., "--gene-a"),
    locus_tag_b: str = typer.Option(..., "--gene-b"),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "locus_tag_a": locus_tag_a,
            "locus_tag_b": locus_tag_b,
            "species_acronym": species_acronym,
        }
    )
    response = client.raw_request("GET", "/api/fitness-correlations/correlation", params=params, format=format)
    handle_raw_response(response, format, title="Gene fitness correlation")

