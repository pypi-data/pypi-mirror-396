"""TTP (Pooled TTP Interactions) CLI commands."""

from __future__ import annotations

from typing import Optional

import typer  # type: ignore[import]

from ..utils import ensure_client, handle_raw_response, merge_params

ttp_app = typer.Typer(help="Pooled TTP interaction endpoints")


@ttp_app.command("metadata")
def ttp_metadata(
    ctx: typer.Context,
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", "/api/ttp/metadata", format=format)
    handle_raw_response(response, format, title="TTP metadata")


@ttp_app.command("search")
def ttp_search(
    ctx: typer.Context,
    query: Optional[str] = typer.Option(None, "--query", "-q"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    sort_field: Optional[str] = typer.Option(None, "--sort-field"),
    sort_order: Optional[str] = typer.Option(None, "--sort-order"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "query": query,
            "page": page,
            "per_page": per_page,
            "sort_field": sort_field,
            "sort_order": sort_order,
        }
    )
    response = client.raw_request("GET", "/api/ttp/search", params=params, format=format)
    handle_raw_response(response, format, title="TTP search")


@ttp_app.command("gene-interactions")
def ttp_gene_interactions(
    ctx: typer.Context,
    locus_tag: str = typer.Argument(...),
    hit_calling: Optional[bool] = typer.Option(None, "--hit-calling"),
    pool_a: Optional[str] = typer.Option(None, "--pool-a"),
    pool_b: Optional[str] = typer.Option(None, "--pool-b"),
    min_ttp_score: Optional[float] = typer.Option(None, "--min-ttp-score"),
    sort_field: Optional[str] = typer.Option(None, "--sort-field"),
    sort_order: Optional[str] = typer.Option(None, "--sort-order"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "locus_tag": locus_tag,
            "hit_calling": hit_calling,
            "poolA": pool_a,
            "poolB": pool_b,
            "min_ttp_score": min_ttp_score,
            "sort_field": sort_field,
            "sort_order": sort_order,
        }
    )
    response = client.raw_request(
        "GET",
        f"/api/ttp/gene/{locus_tag}/interactions",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"TTP interactions ({locus_tag})")


@ttp_app.command("compound-interactions")
def ttp_compound_interactions(
    ctx: typer.Context,
    compound: str = typer.Argument(...),
    hit_calling: Optional[bool] = typer.Option(None, "--hit-calling"),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    isolate_name: Optional[str] = typer.Option(None, "--isolate"),
    min_ttp_score: Optional[float] = typer.Option(None, "--min-ttp-score"),
    sort_field: Optional[str] = typer.Option(None, "--sort-field"),
    sort_order: Optional[str] = typer.Option(None, "--sort-order"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "compound": compound,
            "hit_calling": hit_calling,
            "species_acronym": species_acronym,
            "isolate_name": isolate_name,
            "min_ttp_score": min_ttp_score,
            "sort_field": sort_field,
            "sort_order": sort_order,
        }
    )
    response = client.raw_request(
        "GET",
        f"/api/ttp/compound/{compound}/interactions",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"TTP interactions ({compound})")


@ttp_app.command("hits")
def ttp_hits(
    ctx: typer.Context,
    min_ttp_score: Optional[float] = typer.Option(None, "--min-ttp-score"),
    max_fdr: Optional[float] = typer.Option(None, "--max-fdr"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params({"min_ttp_score": min_ttp_score, "max_fdr": max_fdr})
    response = client.raw_request("GET", "/api/ttp/hits", params=params, format=format)
    handle_raw_response(response, format, title="TTP hits")


@ttp_app.command("pools-analysis")
def ttp_pools_analysis(
    ctx: typer.Context,
    pool_a: str = typer.Option(..., "--pool-a"),
    pool_b: str = typer.Option(..., "--pool-b"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = {"poolA": pool_a, "poolB": pool_b}
    response = client.raw_request("GET", "/api/ttp/pools/analysis", params=params, format=format)
    handle_raw_response(response, format, title="TTP pools analysis")

