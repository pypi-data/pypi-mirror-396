"""Reactions CLI commands."""

from __future__ import annotations

from typing import List, Optional

import typer  # type: ignore[import]

from ..utils import comma_join, ensure_client, handle_raw_response, merge_params

reactions_app = typer.Typer(help="Reaction endpoints")


@reactions_app.command("search")
def reactions_search(
    ctx: typer.Context,
    locus_tags: Optional[List[str]] = typer.Option(None, "--locus-tag"),
    uniprot_ids: Optional[List[str]] = typer.Option(None, "--uniprot"),
    reaction_id: Optional[str] = typer.Option(None, "--reaction-id"),
    metabolite: Optional[str] = typer.Option(None, "--metabolite"),
    substrate: Optional[str] = typer.Option(None, "--substrate"),
    product: Optional[str] = typer.Option(None, "--product"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "locus_tags": comma_join(locus_tags),
            "uniprot_ids": comma_join(uniprot_ids),
            "reaction_id": reaction_id,
            "metabolite": metabolite,
            "substrate": substrate,
            "product": product,
        }
    )
    response = client.raw_request("GET", "/api/reactions/search", params=params, format=format)
    handle_raw_response(response, format, title="Reaction search")

