from autoops.core.job import Job
from autoops.core.registry import Registry
from autoops.core.runner import run


def test_runner_runs_existing_job_and_returns_success():
    def handler():
        return {"value": 42}

    registry = Registry()
    registry.register(Job(name="example", description="Example", handler=handler))

    result = run(registry, "example")

    assert result.success is True
    assert result.data == {"value": 42}
    assert result.error is None


def test_runner_returns_failure_when_job_not_found():
    registry = Registry()

    result = run(registry, "missing")

    assert result.success is False
    assert "not found" in result.message.lower()
    assert result.error is None


def test_runner_captures_exceptions_from_job_handler():
    def handler():
        raise RuntimeError("boom")

    registry = Registry()
    registry.register(Job(name="explode", description="Explodes", handler=handler))

    result = run(registry, "explode")

    assert result.success is False
    assert result.error is not None
    assert isinstance(result.error, RuntimeError)
