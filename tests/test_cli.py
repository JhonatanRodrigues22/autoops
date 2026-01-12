from typer.testing import CliRunner

from autoops.cli import app

runner = CliRunner()


def test_cli_list_shows_example_job():
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "Available jobs" in result.stdout
    assert "example" in result.stdout


def test_cli_run_example_job_shows_success_and_data():
    result = runner.invoke(app, ["run", "example"])

    assert result.exit_code == 0
    assert "✅" in result.stdout
    assert "Job executed successfully" in result.stdout
    assert "Data:" in result.stdout
    assert "Example job executed successfully" in result.stdout


def test_cli_run_missing_job_returns_error():
    result = runner.invoke(app, ["run", "missing_job_name"])

    assert result.exit_code == 1
    assert "❌" in result.stdout
    assert "not found" in result.stdout.lower()
