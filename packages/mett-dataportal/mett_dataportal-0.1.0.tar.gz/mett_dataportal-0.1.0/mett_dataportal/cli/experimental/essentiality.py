"""Essentiality CLI commands."""

from __future__ import annotations

from typing import List, Optional

import typer  # type: ignore[import]

from ..utils import comma_join, ensure_client, handle_raw_response, merge_params

essentiality_app = typer.Typer(help="Essentiality endpoints")


@essentiality_app.command("search")
def essentiality_search(
    ctx: typer.Context,
    locus_tags: Optional[List[str]] = typer.Option(None, "--locus-tag"),
    uniprot_ids: Optional[List[str]] = typer.Option(None, "--uniprot"),
    essentiality_call: Optional[str] = typer.Option(None, "--call"),
    experimental_condition: Optional[str] = typer.Option(None, "--condition"),
    min_tas_in_locus: Optional[int] = typer.Option(None, "--min-tas-in-locus"),
    min_tas_hit: Optional[float] = typer.Option(None, "--min-tas-hit"),
    element: Optional[str] = typer.Option(None, "--element"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "locus_tags": comma_join(locus_tags),
            "uniprot_ids": comma_join(uniprot_ids),
            "essentiality_call": essentiality_call,
            "experimental_condition": experimental_condition,
            "min_tas_in_locus": min_tas_in_locus,
            "min_tas_hit": min_tas_hit,
            "element": element,
        }
    )
    response = client.raw_request("GET", "/api/essentiality/search", params=params, format=format)
    handle_raw_response(response, format, title="Essentiality search")

