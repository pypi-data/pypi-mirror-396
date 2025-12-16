"""Gene CLI commands."""

from __future__ import annotations

from typing import List, Optional

import typer  # type: ignore[import]

from ..utils import comma_join, ensure_client, handle_raw_response, merge_params

genes_app = typer.Typer(help="Gene endpoints")


@genes_app.command("list")
def genes_list(
    ctx: typer.Context,
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    sort_field: Optional[str] = typer.Option(None, "--sort-field"),
    sort_order: Optional[str] = typer.Option(None, "--sort-order"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "page": page,
            "per_page": per_page,
            "sort_field": sort_field,
            "sort_order": sort_order,
        }
    )
    response = client.raw_request("GET", "/api/genes/", params=params, format=format)
    handle_raw_response(response, format, title="Genes")


@genes_app.command("search")
def genes_search(
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
    response = client.raw_request("GET", "/api/genes/search", params=params, format=format)
    handle_raw_response(response, format, title="Gene search")


@genes_app.command("search-advanced")
def genes_search_advanced(
    ctx: typer.Context,
    isolates: Optional[List[str]] = typer.Option(None, "--isolate", "-i"),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    locus_tag: Optional[str] = typer.Option(None, "--locus-tag"),
    query: Optional[str] = typer.Option(None, "--query", "-q"),
    filter: Optional[str] = typer.Option(None, "--filter"),
    filter_operators: Optional[str] = typer.Option(None, "--filter-operators"),
    seq_id: Optional[str] = typer.Option(None, "--seq-id"),
    start_position: Optional[int] = typer.Option(None, "--start-position"),
    end_position: Optional[int] = typer.Option(None, "--end-position"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    sort_field: Optional[str] = typer.Option(None, "--sort-field"),
    sort_order: Optional[str] = typer.Option(None, "--sort-order"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "isolates": comma_join(isolates),
            "species_acronym": species_acronym,
            "locus_tag": locus_tag,
            "query": query,
            "filter": filter,
            "filter_operators": filter_operators,
            "seq_id": seq_id,
            "start_position": start_position,
            "end_position": end_position,
            "page": page,
            "per_page": per_page,
            "sort_field": sort_field,
            "sort_order": sort_order,
        }
    )
    response = client.raw_request("GET", "/api/genes/search/advanced", params=params, format=format)
    handle_raw_response(response, format, title="Advanced gene search")


@genes_app.command("get")
def genes_get(
    ctx: typer.Context,
    locus_tag: str = typer.Argument(..., help="Locus tag"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", f"/api/genes/{locus_tag}", format=format)
    handle_raw_response(response, format, title=f"Gene {locus_tag}")


@genes_app.command("proteomics")
def genes_proteomics(
    ctx: typer.Context,
    locus_tag: str = typer.Argument(...),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", f"/api/genes/{locus_tag}/proteomics", format=format)
    handle_raw_response(response, format, title=f"Proteomics ({locus_tag})")


@genes_app.command("essentiality")
def genes_essentiality(
    ctx: typer.Context,
    locus_tag: str = typer.Argument(...),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", f"/api/genes/{locus_tag}/essentiality", format=format)
    handle_raw_response(response, format, title=f"Essentiality ({locus_tag})")


@genes_app.command("fitness")
def genes_fitness(
    ctx: typer.Context,
    locus_tag: str = typer.Argument(...),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", f"/api/genes/{locus_tag}/fitness", format=format)
    handle_raw_response(response, format, title=f"Fitness ({locus_tag})")


@genes_app.command("mutant-growth")
def genes_mutant_growth(
    ctx: typer.Context,
    locus_tag: str = typer.Argument(...),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", f"/api/genes/{locus_tag}/mutant-growth", format=format)
    handle_raw_response(response, format, title=f"Mutant growth ({locus_tag})")


@genes_app.command("reactions")
def genes_reactions(
    ctx: typer.Context,
    locus_tag: str = typer.Argument(...),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", f"/api/genes/{locus_tag}/reactions", format=format)
    handle_raw_response(response, format, title=f"Reactions ({locus_tag})")


@genes_app.command("correlations")
def genes_correlations(
    ctx: typer.Context,
    locus_tag: str = typer.Argument(...),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    min_correlation: Optional[float] = typer.Option(None, "--min"),
    max_results: Optional[int] = typer.Option(None, "--max-results"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "species_acronym": species_acronym,
            "min_correlation": min_correlation,
            "max_results": max_results,
        }
    )
    response = client.raw_request(
        "GET",
        f"/api/genes/{locus_tag}/correlations",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"Correlations ({locus_tag})")


@genes_app.command("orthologs")
def genes_orthologs(
    ctx: typer.Context,
    locus_tag: str = typer.Argument(...),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    orthology_type: Optional[str] = typer.Option(None, "--orthology-type"),
    one_to_one_only: Optional[bool] = typer.Option(None, "--one-to-one-only"),
    cross_species_only: Optional[bool] = typer.Option(None, "--cross-species-only"),
    max_results: Optional[int] = typer.Option(None, "--max-results"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "species_acronym": species_acronym,
            "orthology_type": orthology_type,
            "one_to_one_only": one_to_one_only,
            "cross_species_only": cross_species_only,
            "max_results": max_results,
        }
    )
    response = client.raw_request(
        "GET",
        f"/api/genes/{locus_tag}/orthologs",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"Orthologs ({locus_tag})")


@genes_app.command("operons")
def genes_operons(
    ctx: typer.Context,
    locus_tag: str = typer.Argument(...),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params({"species_acronym": species_acronym})
    response = client.raw_request(
        "GET",
        f"/api/genes/{locus_tag}/operons",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"Operons ({locus_tag})")


@genes_app.command("autocomplete")
def genes_autocomplete(
    ctx: typer.Context,
    query: str = typer.Option(..., "--query", "-q"),
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    isolates: Optional[List[str]] = typer.Option(None, "--isolates", "-i"),
    filter: Optional[str] = typer.Option(None, "--filter", help="Filter expression (e.g., 'essentiality:essential')"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    per_page: Optional[int] = typer.Option(None, "--per-page"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "query": query,
            "species_acronym": species_acronym,
            "isolates": comma_join(isolates),
            "filter": filter,
            "page": page,
            "per_page": per_page,
        }
    )
    response = client.raw_request("GET", "/api/genes/autocomplete", params=params, format=format)
    handle_raw_response(response, format, title="Gene autocomplete")


@genes_app.command("faceted-search")
def genes_faceted_search(
    ctx: typer.Context,
    species_acronym: Optional[str] = typer.Option(None, "--species", "-s"),
    limit: Optional[int] = typer.Option(None, "--limit"),
    pfam: Optional[str] = typer.Option(None, "--pfam"),
    interpro: Optional[str] = typer.Option(None, "--interpro"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "species_acronym": species_acronym,
            "limit": limit,
            "pfam": pfam,
            "interpro": interpro,
        }
    )
    response = client.raw_request("GET", "/api/genes/faceted-search", params=params, format=format)
    handle_raw_response(response, format, title="Gene facets")


@genes_app.command("protein")
def genes_protein(
    ctx: typer.Context,
    protein_id: str = typer.Argument(..., help="Protein ID"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", f"/api/genes/protein/{protein_id}", format=format)
    handle_raw_response(response, format, title=f"Protein {protein_id}")

