from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from autoops.core.job import Job


@dataclass
class Registry:
    """
    In-memory registry of jobs.
    """

    _jobs: Dict[str, Job] = field(default_factory=dict)

    def register(self, job: Job) -> None:
        """
        Register a job. Raises ValueError if the name already exists.
        """
        if job.name in self._jobs:
            raise ValueError(f"Job '{job.name}' is already registered")
        self._jobs[job.name] = job

    def get(self, name: str) -> Optional[Job]:
        """
        Get a job by name. Returns None if it doesn't exist.
        """
        return self._jobs.get(name)

    def list_names(self) -> List[str]:
        """
        List all registered job names.
        """
        return sorted(self._jobs.keys())
