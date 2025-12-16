"""Proteomics CLI commands."""

from __future__ import annotations

from typing import List, Optional

import typer  # type: ignore[import]

from ..utils import comma_join, ensure_client, handle_raw_response, merge_params

proteomics_app = typer.Typer(help="Proteomics endpoints")


@proteomics_app.command("search")
def proteomics_search(
    ctx: typer.Context,
    locus_tags: Optional[List[str]] = typer.Option(None, "--locus-tag"),
    uniprot_ids: Optional[List[str]] = typer.Option(None, "--uniprot"),
    min_coverage: Optional[float] = typer.Option(None, "--min-coverage"),
    min_unique_peptides: Optional[int] = typer.Option(None, "--min-unique-peptides"),
    has_evidence: Optional[bool] = typer.Option(None, "--has-evidence"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "locus_tags": comma_join(locus_tags),
            "uniprot_ids": comma_join(uniprot_ids),
            "min_coverage": min_coverage,
            "min_unique_peptides": min_unique_peptides,
            "has_evidence": has_evidence,
        }
    )
    response = client.raw_request("GET", "/api/proteomics/search", params=params, format=format)
    handle_raw_response(response, format, title="Proteomics search")

