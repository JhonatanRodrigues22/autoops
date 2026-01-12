from autoops.core.job import Job
from autoops.core.registry import Registry


def _noop():
    return None


def test_registry_can_register_and_list_jobs():
    registry = Registry()
    job = Job(name="example", description="Example job", handler=_noop)

    registry.register(job)

    names = registry.list_names()
    assert "example" in names


def test_registry_rejects_duplicate_job_names():
    registry = Registry()
    job1 = Job(name="dup", description="Job 1", handler=_noop)
    job2 = Job(name="dup", description="Job 2", handler=_noop)

    registry.register(job1)

    try:
        registry.register(job2)
        assert False, "Expected ValueError for duplicate job name"
    except ValueError:
        assert True


def test_registry_get_returns_job_or_none():
    registry = Registry()
    job = Job(name="example", description="Example job", handler=_noop)
    registry.register(job)

    assert registry.get("example") is job
    assert registry.get("missing") is None
