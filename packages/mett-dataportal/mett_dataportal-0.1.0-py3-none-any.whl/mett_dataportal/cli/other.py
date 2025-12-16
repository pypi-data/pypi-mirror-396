"""Other CLI commands (PyHMMER and raw API access)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional

import typer  # type: ignore[import]

from .utils import comma_join, ensure_client, handle_raw_response, merge_params, parse_key_value_pairs

api_app = typer.Typer(help="Low-level raw API access")
pyhmmer_app = typer.Typer(help="PyHMMER endpoints")


def _load_body_json(body: Optional[str], body_file: Optional[Path]) -> Optional[Any]:
    if body and body_file:
        raise typer.BadParameter("Use either --body-json or --body-file, not both")
    if body:
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise typer.BadParameter(f"Invalid JSON payload: {exc}") from exc
    if body_file:
        return json.loads(body_file.read_text())
    return None


@api_app.command("request")
def api_request(
    ctx: typer.Context,
    method: str = typer.Argument(..., help="HTTP method (GET, POST, etc.)"),
    path: str = typer.Argument(..., help="API path, e.g. /api/species/"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Response format: json|tsv"),
    query: Optional[List[str]] = typer.Option(None, "--query", "-q", help="Query parameter KEY=VALUE"),
    header: Optional[List[str]] = typer.Option(None, "--header", "-H", help="Extra header KEY:VALUE"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="Raw request payload"),
    json_body: Optional[str] = typer.Option(None, "--json", help="JSON request payload"),
) -> None:
    """Invoke any METT API endpoint while reusing client configuration."""

    client = ensure_client(ctx)

    if data and json_body:
        raise typer.BadParameter("Use either --data or --json, not both")

    query_params = parse_key_value_pairs(query)
    header_params = parse_key_value_pairs(
        header,
        separator=":",
        error_message="Expected header format KEY:VALUE",
    )

    json_payload: Any = None
    if json_body:
        try:
            json_payload = json.loads(json_body)
        except json.JSONDecodeError as exc:
            raise typer.BadParameter(f"Invalid JSON payload: {exc}") from exc

    response = client.raw_request(
        method=method,
        path=path,
        params=query_params,
        headers=header_params,
        data=data,
        json_body=json_payload,
        format=format,
    )

    handle_raw_response(response, format, title=f"{method.upper()} {path}")


@pyhmmer_app.command("databases")
def pyhmmer_databases(
    ctx: typer.Context,
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", "/api/pyhmmer/search/databases", format=format)
    handle_raw_response(response, format, title="PyHMMER databases")


@pyhmmer_app.command("mx-choices")
def pyhmmer_mx_choices(
    ctx: typer.Context,
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", "/api/pyhmmer/search/mx-choices", format=format)
    handle_raw_response(response, format, title="PyHMMER mx choices")


@pyhmmer_app.command("search")
def pyhmmer_search(
    ctx: typer.Context,
    body_json: Optional[str] = typer.Option(None, "--body-json", help="Inline JSON payload"),
    body_file: Optional[Path] = typer.Option(None, "--body-file", exists=True, readable=True, help="Path to JSON body"),
    format: Optional[str] = typer.Option("json", "--format", "-f", help="json|tsv"),
) -> None:
    client = ensure_client(ctx)
    payload = _load_body_json(body_json, body_file)
    if payload is None:
        raise typer.BadParameter("Provide --body-json or --body-file")
    response = client.raw_request(
        "POST",
        "/api/pyhmmer/search",
        json_body=payload,
        format=format,
    )
    handle_raw_response(response, format, title="PyHMMER search")


@pyhmmer_app.command("result")
def pyhmmer_result(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="PyHMMER job ID"),
    page: Optional[int] = typer.Option(None, "--page", "-p"),
    page_size: Optional[int] = typer.Option(None, "--page-size"),
    taxonomy_ids: Optional[List[str]] = typer.Option(None, "--taxonomy-id"),
    architecture: Optional[str] = typer.Option(None, "--architecture"),
    with_domains: Optional[bool] = typer.Option(None, "--with-domains"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = merge_params(
        {
            "page": page,
            "page_size": page_size,
            "taxonomy_ids": comma_join(taxonomy_ids),
            "architecture": architecture,
            "with_domains": with_domains,
        }
    )
    response = client.raw_request(
        "GET",
        f"/api/pyhmmer/result/{job_id}",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"PyHMMER result ({job_id})")


@pyhmmer_app.command("domains")
def pyhmmer_domains(
    ctx: typer.Context,
    job_id: str = typer.Argument(...),
    target: str = typer.Option(..., "--target"),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    params = {"target": target}
    response = client.raw_request(
        "GET",
        f"/api/pyhmmer/result/{job_id}/domains",
        params=params,
        format=format,
    )
    handle_raw_response(response, format, title=f"PyHMMER domains ({job_id})")


@pyhmmer_app.command("download")
def pyhmmer_download(
    ctx: typer.Context,
    job_id: str = typer.Argument(...),
    download_format: str = typer.Option(..., "--download-format", help="aligned_fasta|fasta|csv|tab"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    client = ensure_client(ctx)
    params = {"format": download_format}
    response = client.raw_request(
        "GET",
        f"/api/pyhmmer/result/{job_id}/download",
        params=params,
        format="tsv" if download_format == "tab" else None,
    )
    content = response.text
    if output:
        output.write_text(content)
        typer.echo(f"Wrote {output}")
    else:
        typer.echo(content)


@pyhmmer_app.command("debug-msa")
def pyhmmer_debug_msa(
    ctx: typer.Context,
    job_id: str = typer.Argument(...),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request(
        "GET",
        f"/api/pyhmmer/result/{job_id}/debug-pyhmmer-msa",
        format=format,
    )
    handle_raw_response(response, format, title=f"PyHMMER MSA ({job_id})")


@pyhmmer_app.command("debug-fasta")
def pyhmmer_debug_fasta(
    ctx: typer.Context,
    job_id: str = typer.Argument(...),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request(
        "GET",
        f"/api/pyhmmer/result/{job_id}/debug-fasta",
        format=format,
    )
    handle_raw_response(response, format, title=f"PyHMMER FASTA ({job_id})")


@pyhmmer_app.command("debug-task")
def pyhmmer_debug_task(
    ctx: typer.Context,
    task_id: str = typer.Argument(...),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", f"/api/pyhmmer/debug/task/{task_id}", format=format)
    handle_raw_response(response, format, title=f"PyHMMER task ({task_id})")


@pyhmmer_app.command("testtask")
def pyhmmer_testtask(
    ctx: typer.Context,
    body_json: Optional[str] = typer.Option(None, "--body-json"),
    body_file: Optional[Path] = typer.Option(None, "--body-file", exists=True, readable=True),
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    payload = _load_body_json(body_json, body_file)
    response = client.raw_request("POST", "/api/pyhmmer/testtask", json_body=payload, format=format)
    handle_raw_response(response, format, title="PyHMMER test task")

