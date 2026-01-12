from __future__ import annotations

import builtins
import json
from pathlib import Path
from typing import Optional

import typer

from autoops.config.loader import load_organize_files_config
from autoops.core.job import Job
from autoops.core.registry import Registry
from autoops.jobs.example import example_handler
from autoops.jobs.organize_files import organize_files

app = typer.Typer(
    name="autoops",
    help="AutoOps - Organized and scalable automation orchestrator",
    no_args_is_help=True,
)


def build_registry(
    *,
    config_path: Optional[Path] = None,
    source_dir: Optional[Path] = None,
    destination_dir: Optional[Path] = None,
    dry_run: bool = True,
    preview: bool = False,
) -> Registry:
    """
    Builds and returns a registry with all available jobs.
    """
    registry = Registry()

    # Example job
    registry.register(
        Job(
            name="example",
            description="Example job for demonstration purposes",
            handler=example_handler,
        )
    )

    # organize-files job (configurable via YAML + CLI overrides)
    cfg_file = config_path or Path("configs/organize_files.yaml")
    loaded = load_organize_files_config(
        cfg_file,
        source_dir=source_dir,
        destination_dir=destination_dir,
        dry_run=dry_run,
    )

    def organize_handler():
        # preview = show what would be moved, without touching files
        effective_dry_run = True if preview else loaded.dry_run

        return organize_files(
            source_dir=loaded.source_dir,
            destination_dir=loaded.destination_dir,
            categories=loaded.categories,
            others_dir=loaded.others_dir,
            dry_run=effective_dry_run,
            preview=preview,
        )

    registry.register(
        Job(
            name="organize-files",
            description="Organize files into categorized folders",
            handler=organize_handler,
        )
    )

    return registry


def _safe_to_dict(obj) -> dict:
    """
    Best-effort conversion to dict for pretty JSON output.
    Supports:
      - dict already
      - objects with .data/.success/.message/.error
      - objects with __dict__
    """
    if isinstance(obj, dict):
        return obj

    d = {}
    for key in ("success", "message", "data", "error"):
        if hasattr(obj, key):
            d[key] = getattr(obj, key)

    if d:
        return d

    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)

    return {"value": str(obj)}


def _print_human_job_summary(
    *,
    job_name: str,
    result,
    preview: bool,
    max_preview: int,
) -> None:
    """
    Print a human-friendly summary for a JobResult-like object.
    """
    d = _safe_to_dict(result)
    data = d.get("data") or {}

    ok = bool(d.get("success", True))
    header_icon = "✅" if ok else "❌"
    mode = "PREVIEW" if preview else ("DRY-RUN" if data.get("dry_run") else "RUN")

    typer.echo(f"{header_icon} {job_name} ({mode})")

    source = data.get("source_dir")
    dest = data.get("destination_dir")
    if source:
        typer.echo(f"Source: {source}")
    if dest:
        typer.echo(f"Destination: {dest}")

    moved_total = data.get("moved_total")
    if moved_total is not None:
        label = "Would move" if preview or data.get("dry_run") else "Moved"
        typer.echo(f"\n{label}: {moved_total} file(s)")

    moved_by_category = data.get("moved_by_category") or {}
    if isinstance(moved_by_category, dict) and moved_by_category:
        non_zero = {k: v for k, v in moved_by_category.items() if int(v) > 0}
        if non_zero:
            for k, v in sorted(non_zero.items(), key=lambda kv: (-kv[1], kv[0])):
                typer.echo(f"  {k}: {v}")

    preview_moves = data.get("preview_moves") or []
    if preview and preview_moves:
        typer.echo("\nPreview moves:")
        shown = 0
        for item in preview_moves:
            if shown >= max_preview:
                remaining = len(preview_moves) - shown
                typer.echo(f"  ... and {remaining} more")
                break

            # IMPORTANT: builtins.list is used because we have a CLI command named "list"
            if isinstance(item, (builtins.list, builtins.tuple)) and len(item) == 2:
                src_name, dst_rel = item
                typer.echo(f"  {src_name}  ->  {dst_rel}")
            else:
                typer.echo(f"  {item}")

            shown += 1

    err = d.get("error")
    if err:
        typer.secho(f"\nError: {err}", fg=typer.colors.RED)


@app.command()
def version() -> None:
    """
    Show the current version of AutoOps.
    """
    typer.echo("AutoOps version 0.1.0")


@app.command("list")
def list_jobs() -> None:
    """
    List available jobs.
    """
    registry = build_registry()
    for name in registry.list_names():
        typer.echo(name)


@app.command()
def run(
    job_name: str = typer.Argument(..., help="Job name to run (use: autoops list)"),
    config: Optional[Path] = typer.Option(
        None, "--config", help="Path to a YAML config file"
    ),
    source_dir: Optional[Path] = typer.Option(
        None, "--source-dir", help="Override the source directory"
    ),
    destination_dir: Optional[Path] = typer.Option(
        None, "--destination-dir", help="Override the destination directory"
    ),
    dry_run: bool = typer.Option(
        True, "--dry-run/--no-dry-run", help="Do not move files (default: dry-run)"
    ),
    preview: bool = typer.Option(
        False, "--preview", help="Show what would be moved without touching files"
    ),
    json_out: bool = typer.Option(
        False, "--json", help="Print full JSON output (developer/automation friendly)"
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        help="Print nothing (exit code still indicates success/failure)",
    ),
    max_preview: int = typer.Option(
        20, "--max-preview", min=0, help="Max preview items to print (0 = none)"
    ),
) -> None:
    """
    Run a job by name.
    """
    if job_name == "organize-files":
        if destination_dir is None and source_dir is not None:
            destination_dir = source_dir

    registry = build_registry(
        config_path=config,
        source_dir=source_dir,
        destination_dir=destination_dir,
        dry_run=dry_run,
        preview=preview,
    )

    job = registry.get(job_name)
    if job is None:
        if not quiet:
            typer.secho(f"❌ Job not found: {job_name}", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    result = job.run()

    if quiet:
        d = _safe_to_dict(result)
        ok = bool(d.get("success", True))
        raise typer.Exit(code=0 if ok else 1)

    if json_out:
        d = _safe_to_dict(result)
        typer.echo(json.dumps(d, ensure_ascii=False, indent=2))
        return

    _print_human_job_summary(
        job_name=job_name,
        result=result,
        preview=preview,
        max_preview=max_preview,
    )


def entry() -> None:
    """
    Console entry point (used by [project.scripts]).
    """
    app()


if __name__ == "__main__":
    entry()
