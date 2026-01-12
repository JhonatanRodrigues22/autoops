from __future__ import annotations

import json
from importlib.metadata import PackageNotFoundError, version as pkg_version
from typing import Optional

import typer

from autoops.core.registry import Registry
from autoops.core.runner import run as run_job
from autoops.jobs.example import example_job

app = typer.Typer(
    name="autoops",
    help="AutoOps - Organized and scalable automation orchestrator",
)


@app.callback()
def cli() -> None:
    """
    AutoOps CLI.

    Keeps the CLI in multi-command mode and acts as the root command group.
    """
    return


def build_registry() -> Registry:
    """
    Build a registry for the current execution.
    For now, jobs are registered explicitly (no magic scanning).
    """
    registry = Registry()
    registry.register(example_job)
    return registry


@app.command()
def version() -> None:
    """Show the current version of AutoOps."""
    try:
        v = pkg_version("autoops")
    except PackageNotFoundError:
        v = "0.0.0"
    typer.echo(f"AutoOps version {v}")


@app.command("list")
def list_jobs() -> None:
    """List available jobs."""
    registry = build_registry()
    names = registry.list_names()

    if not names:
        typer.echo("No jobs registered.")
        raise typer.Exit(code=0)

    typer.echo("Available jobs:")
    for name in names:
        job = registry.get(name)
        desc = job.description if job else ""
        typer.echo(f"  - {name}: {desc}")


@app.command()
def run(
    job_name: str = typer.Argument(..., help="Name of the job to execute"),
    show_data: bool = typer.Option(True, "--data/--no-data", help="Show job returned data"),
) -> None:
    """Run a job by name."""
    registry = build_registry()
    result = run_job(registry, job_name)

    if result.success:
        typer.echo(f"✅ {result.message}")
        if show_data and result.data is not None:
            try:
                typer.echo("Data:")
                typer.echo(json.dumps(result.data, ensure_ascii=False, indent=2))
            except TypeError:
                typer.echo("Data (raw):")
                typer.echo(str(result.data))
        raise typer.Exit(code=0)

    typer.echo(f"❌ {result.message}")
    if result.error is not None:
        typer.echo(f"Error: {type(result.error).__name__}: {result.error}")
    raise typer.Exit(code=1)


def entry() -> None:
    """Console script entry point."""
    app()


if __name__ == "__main__":
    entry()
