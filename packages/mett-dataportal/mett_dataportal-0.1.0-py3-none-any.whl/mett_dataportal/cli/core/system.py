"""System and metadata CLI commands."""

from __future__ import annotations

from typing import Optional

import typer  # type: ignore[import]

from ..utils import ensure_client, handle_raw_response

system_app = typer.Typer(help="System / metadata endpoints")


@system_app.command("health")
def system_health(
    ctx: typer.Context,
    format: Optional[str] = typer.Option(None, "--format", "-f", help="json|tsv"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", "/api/health", format=format)
    handle_raw_response(response, format, title="Health Check")


@system_app.command("features")
def system_features(
    ctx: typer.Context,
    format: Optional[str] = typer.Option(None, "--format", "-f", help="json|tsv"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", "/api/features", format=format)
    handle_raw_response(response, format, title="Feature Flags")


@system_app.command("cog-categories")
def system_cog_categories(
    ctx: typer.Context,
    format: Optional[str] = typer.Option(None, "--format", "-f"),
) -> None:
    client = ensure_client(ctx)
    response = client.raw_request("GET", "/api/metadata/cog-categories", format=format)
    handle_raw_response(response, format, title="COG Categories")

