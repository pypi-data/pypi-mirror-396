"""Drug CLI commands."""

from __future__ import annotations

from typing import Optional

import typer  # type: ignore[import]

from ..output import print_full_table, print_json, print_tsv
from ..utils import ensure_client, handle_raw_response, merge_params

drugs_app = typer.Typer(help="Drug endpoints")


@drugs_app.command("mic")
def drug_mic_search(
    ctx: typer.Context,
    query: Optional[str] = typer.Option(None, "--query", "-q"),
    drug_name: Optional[str] = typer.Option(None, "--drug-name"),
    drug_class: Optional[str] = typer.Option(None, "--drug-class"),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    min_mic_value: Optional[float] = typer.Option(None, "--min-mic-value"),
    max_mic_value: Optional[float] = typer.Option(None, "--max-mic-value"),
    unit: Optional[str] = typer.Option(None, "--unit"),
    experimental_condition: Optional[str] = typer.Option(None, "--condition"),
    page: int = typer.Option(1, "--page", "-p"),
    per_page: int = typer.Option(20, "--per-page"),
    sort_by: Optional[str] = typer.Option(None, "--sort-by"),
    sort_order: Optional[str] = typer.Option(None, "--sort-order"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json|tsv (default: table)"),
) -> None:
    client = ensure_client(ctx)
    api_format = format or "json"  # Default to JSON for API request
    result = client.search_drug_mic(
        format=api_format,
        query=query,
        drug_name=drug_name,
        drug_class=drug_class,
        species_acronym=species_acronym,
        min_mic_value=min_mic_value,
        max_mic_value=max_mic_value,
        unit=unit,
        experimental_condition=experimental_condition,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    if format == "tsv":
        print_tsv(result.items)
    elif format == "json":
        print_json(result.raw)
    else:
        # No format specified - display as table
        print_full_table(result.items, title="Drug MIC")


@drugs_app.command("mic-by-drug")
def drug_mic_by_drug(
    ctx: typer.Context,
    drug_name: str = typer.Argument(..., help="Drug name"),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params({"species_acronym": species_acronym})
    response = client.raw_request(
        "GET",
        f"/api/drugs/mic/by-drug/{drug_name}",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"Drug MIC ({drug_name})")


@drugs_app.command("metabolism-search")
def drug_metabolism_search(
    ctx: typer.Context,
    query: Optional[str] = typer.Option(None, "--query", "-q"),
    drug_name: Optional[str] = typer.Option(None, "--drug-name"),
    drug_class: Optional[str] = typer.Option(None, "--drug-class"),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    min_fdr: Optional[float] = typer.Option(None, "--min-fdr"),
    min_degr_percent: Optional[float] = typer.Option(None, "--min-degr-percent"),
    metabolizer_classification: Optional[str] = typer.Option(None, "--classification"),
    is_significant: Optional[bool] = typer.Option(None, "--significant"),
    experimental_condition: Optional[str] = typer.Option(None, "--condition"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    sort_by: Optional[str] = typer.Option(None, "--sort-by"),
    sort_order: Optional[str] = typer.Option(None, "--sort-order"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "query": query,
            "drug_name": drug_name,
            "drug_class": drug_class,
            "species_acronym": species_acronym,
            "min_fdr": min_fdr,
            "min_degr_percent": min_degr_percent,
            "metabolizer_classification": metabolizer_classification,
            "is_significant": is_significant,
            "experimental_condition": experimental_condition,
            "page": page,
            "per_page": per_page,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
    )
    response = client.raw_request("GET", "/api/drugs/metabolism/search", params=params, format=format)
    handle_raw_response(response, format, title="Drug metabolism search")


@drugs_app.command("metabolism-by-drug")
def drug_metabolism_by_drug(
    ctx: typer.Context,
    drug_name: str = typer.Argument(..., help="Drug name"),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params({"species_acronym": species_acronym})
    response = client.raw_request(
        "GET",
        f"/api/drugs/metabolism/by-drug/{drug_name}",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"Drug metabolism ({drug_name})")


@drugs_app.command("mic-by-class")
def drug_mic_by_class(
    ctx: typer.Context,
    drug_class: str = typer.Argument(...),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "species_acronym": species_acronym,
            "page": page,
            "per_page": per_page,
        }
    )
    response = client.raw_request(
        "GET",
        f"/api/drugs/mic/by-class/{drug_class}",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"Drug MIC class ({drug_class})")


@drugs_app.command("metabolism-by-class")
def drug_metabolism_by_class(
    ctx: typer.Context,
    drug_class: str = typer.Argument(...),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "species_acronym": species_acronym,
            "page": page,
            "per_page": per_page,
        }
    )
    response = client.raw_request(
        "GET",
        f"/api/drugs/metabolism/by-class/{drug_class}",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"Drug metabolism class ({drug_class})")

