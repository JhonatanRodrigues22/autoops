from __future__ import annotations

import json
from importlib.metadata import PackageNotFoundError, version as pkg_version
from pathlib import Path
from typing import Optional

import typer

from autoops.config.loader import load_organize_files_config
from autoops.core.paths import get_default_downloads_dir
from autoops.core.registry import Registry
from autoops.core.runner import run as run_job
from autoops.jobs.example import example_job
from autoops.jobs.organize_files import OrganizeFilesConfig, make_organize_files_job

app = typer.Typer(
    name="autoops",
    help="AutoOps - Organized and scalable automation orchestrator",
)


@app.callback()
def cli() -> None:
    """
    AutoOps CLI root command group.
    """
    return


def build_registry(
    *,
    config_path: Optional[Path] = None,
    source_dir: Optional[Path] = None,
    destination_dir: Optional[Path] = None,
    dry_run: Optional[bool] = None,
) -> Registry:
    """
    Build a registry for the current execution.
    Jobs are registered explicitly and may be configured per execution.
    """
    registry = Registry()

    # Simple demo job
    registry.register(example_job)

    # organize-files job (configurable)
    cfg_file = config_path or Path("configs/organize_files.yaml")
    loaded = load_organize_files_config(
        cfg_file,
        source_dir=source_dir,
        destination_dir=destination_dir,
        dry_run=dry_run,
    )

    organize_cfg = OrganizeFilesConfig(
        source_dir=loaded.source_dir,
        destination_dir=loaded.destination_dir,  # will default to source_dir when omitted
        dry_run=loaded.dry_run,
        categories=loaded.categories,
        others_dir=loaded.others_dir,
    )
    registry.register(make_organize_files_job(organize_cfg))

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


def _prompt_for_source_dir(default_downloads: Path) -> Path:
    """
    Interactive chooser:
    1) Use Downloads
    2) Enter a path
    """
    typer.echo("Choose where to run 'organize-files':")
    typer.echo(f"  1) Default Downloads: {default_downloads}")
    typer.echo("  2) Enter a folder path")
    choice = typer.prompt("Option", default="1").strip()

    if choice == "1":
        return default_downloads

    if choice == "2":
        raw = typer.prompt("Enter folder path").strip().strip('"')
        return Path(raw).expanduser().resolve()

    typer.echo("Invalid option. Using Downloads.")
    return default_downloads


@app.command()
def run(
    job_name: str = typer.Argument(..., help="Name of the job to execute"),
    config: Optional[Path] = typer.Option(
        None, "--config", help="Path to YAML config (used by jobs that support config)"
    ),
    source_dir: Optional[Path] = typer.Option(
        None, "--source-dir", help="Override source dir (organize-files)"
    ),
    destination_dir: Optional[Path] = typer.Option(
        None, "--destination-dir", help="Override destination dir (organize-files)"
    ),
    dry_run: Optional[bool] = typer.Option(
        None, "--dry-run/--no-dry-run", help="Override dry-run (organize-files)"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", help="Interactive mode to choose the folder for organize-files"
    ),
    show_data: bool = typer.Option(True, "--data/--no-data", help="Show job returned data"),
) -> None:
    """Run a job by name."""
    # Smart default for organize-files:
    # If user didn't pass --source-dir and asked interactive, prompt.
    # If user didn't pass --source-dir and didn't ask interactive, default to Downloads.
    if job_name == "organize-files" and source_dir is None:
        downloads = get_default_downloads_dir()
        source_dir = _prompt_for_source_dir(downloads) if interactive else downloads

    # If organize-files and destination_dir not provided, keep it in the same folder as source.
    if job_name == "organize-files" and destination_dir is None and source_dir is not None:
        destination_dir = source_dir

    registry = build_registry(
        config_path=config,
        source_dir=source_dir,
        destination_dir=destination_dir,
        dry_run=dry_run,
    )
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
