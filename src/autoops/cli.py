from importlib.metadata import PackageNotFoundError, version as pkg_version

import typer

app = typer.Typer(
    name="autoops",
    help="AutoOps - Organized and scalable automation orchestrator",
)


@app.callback()
def cli() -> None:
    """
    AutoOps CLI.

    This callback forces Typer to keep a multi-command CLI structure,
    even when there is only one real command implemented.
    """
    # No logic here on purpose.
    return


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
    """
    List available jobs.

    (Stub for now — will be connected to the registry in Checkpoint 3.)
    """
    typer.echo("No jobs registered yet. (Coming in Checkpoint 3)")


def entry() -> None:
    """Console script entry point."""
    app()


if __name__ == "__main__":
    entry()
