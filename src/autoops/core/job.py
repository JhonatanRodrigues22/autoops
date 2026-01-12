from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class JobResult:
    success: bool
    message: str
    data: Any = None
    error: Optional[BaseException] = None


@dataclass(frozen=True)
class Job:
    name: str
    description: str
    handler: Callable[[], Any]

    def run(self) -> JobResult:
        """
        Execute the job handler and wrap the outcome into a JobResult.
        """
        try:
            result = self.handler()

            # Allow handlers to return a JobResult directly (advanced use-case)
            if isinstance(result, JobResult):
                return result

            return JobResult(
                success=True,
                message="Job executed successfully",
                data=result,
                error=None,
            )
        except BaseException as exc:  # intentional: we want to capture any runtime failure
            return JobResult(
                success=False,
                message="Job execution failed",
                data=None,
                error=exc,
            )
