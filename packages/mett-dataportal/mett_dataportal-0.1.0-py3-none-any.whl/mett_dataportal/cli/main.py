"""Typer-based CLI wired into the high-level DataPortalClient."""

from __future__ import annotations

from typing import Optional

import typer  # type: ignore[import]

from .core import genes_app, genomes_app, species_app, system_app
from .experimental import (
    drugs_app,
    essentiality_app,
    fitness_app,
    fitness_corr_app,
    mutant_app,
    operons_app,
    orthologs_app,
    proteomics_app,
    reactions_app,
)
from .interactions import ppi_app, ttp_app
from .other import api_app, pyhmmer_app
from .utils import _build_client

app = typer.Typer(help="METT Data Portal CLI")

# Register all sub-apps
app.add_typer(system_app, name="system")
app.add_typer(species_app, name="species")
app.add_typer(genomes_app, name="genomes")
app.add_typer(genes_app, name="genes")
app.add_typer(drugs_app, name="drugs")
app.add_typer(proteomics_app, name="proteomics")
app.add_typer(essentiality_app, name="essentiality")
app.add_typer(fitness_app, name="fitness")
app.add_typer(fitness_corr_app, name="fitness-correlations")
app.add_typer(mutant_app, name="mutant-growth")
app.add_typer(reactions_app, name="reactions")
app.add_typer(operons_app, name="operons")
app.add_typer(orthologs_app, name="orthologs")
app.add_typer(ttp_app, name="ttp")
app.add_typer(ppi_app, name="ppi")
app.add_typer(pyhmmer_app, name="pyhmmer")
app.add_typer(api_app, name="api")


@app.callback()
def main(
    ctx: typer.Context,
    base_url: Optional[str] = typer.Option(None, help="Override the API base URL"),
    jwt: Optional[str] = typer.Option(None, help="JWT token for experimental endpoints"),
    timeout: Optional[int] = typer.Option(None, help="HTTP timeout (seconds)"),
    verify_ssl: Optional[bool] = typer.Option(None, help="Set false to skip TLS verification"),
) -> None:
    """Initialize shared client and stash in Typer context."""

    ctx.obj = _build_client(
        base_url=base_url,
        jwt=jwt,
        timeout=timeout,
        verify_ssl=verify_ssl,
    )


if __name__ == "__main__":
    app()
