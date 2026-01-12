from __future__ import annotations

from autoops.core.job import JobResult
from autoops.core.registry import Registry


def run(registry: Registry, job_name: str) -> JobResult:
    """
    Execute a job by name using the provided registry.
    Returns a JobResult with success/failure details.
    """
    job = registry.get(job_name)
    if job is None:
        return JobResult(
            success=False,
            message=f"Job '{job_name}' not found",
            data=None,
            error=None,
        )

    return job.run()
