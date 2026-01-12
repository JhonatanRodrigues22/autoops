from typer.testing import CliRunner

from autoops.cli import app

runner = CliRunner()


def test_cli_list_shows_jobs():
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "example" in result.stdout
    assert "organize-files" in result.stdout


def test_cli_run_example_job_shows_success():
    result = runner.invoke(app, ["run", "example"])
    assert result.exit_code == 0
    assert "✅" in result.stdout
    # output novo é humano e curto
    assert "example" in result.stdout
    assert "(RUN)" in result.stdout


def test_cli_run_example_job_json_output_contains_message():
    result = runner.invoke(app, ["run", "example", "--json"])
    assert result.exit_code == 0
    # no modo json, a mensagem completa deve existir
    assert "Job executed successfully" in result.stdout


def test_cli_run_missing_job_returns_error_exit_code_2():
    result = runner.invoke(app, ["run", "missing_job_name"])
    assert result.exit_code == 2
    assert "❌" in result.stdout
    assert "not found" in result.stdout.lower()
