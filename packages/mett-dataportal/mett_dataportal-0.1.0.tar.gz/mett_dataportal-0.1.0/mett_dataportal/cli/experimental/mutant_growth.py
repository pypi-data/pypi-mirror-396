"""Mutant growth CLI commands."""

from __future__ import annotations

from typing import List, Optional

import typer  # type: ignore[import]

from ..utils import comma_join, ensure_client, handle_raw_response, merge_params

mutant_app = typer.Typer(help="Mutant growth endpoints")


@mutant_app.command("search")
def mutant_growth_search(
    ctx: typer.Context,
    locus_tags: Optional[List[str]] = typer.Option(None, "--locus-tag"),
    uniprot_ids: Optional[List[str]] = typer.Option(None, "--uniprot"),
    media: Optional[str] = typer.Option(None, "--media"),
    experimental_condition: Optional[str] = typer.Option(None, "--condition"),
    min_doubling_time: Optional[float] = typer.Option(None, "--min-doubling-time"),
    max_doubling_time: Optional[float] = typer.Option(None, "--max-doubling-time"),
    exclude_double_picked: Optional[bool] = typer.Option(None, "--exclude-double-picked"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "locus_tags": comma_join(locus_tags),
            "uniprot_ids": comma_join(uniprot_ids),
            "media": media,
            "experimental_condition": experimental_condition,
            "min_doubling_time": min_doubling_time,
            "max_doubling_time": max_doubling_time,
            "exclude_double_picked": exclude_double_picked,
        }
    )
    response = client.raw_request("GET", "/api/mutant-growth/search", params=params, format=format)
    handle_raw_response(response, format, title="Mutant growth search")

