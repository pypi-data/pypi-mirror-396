from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
    from luna_quantum.solve.domain.solve_job import SolveJob


class ISolveJobGetByIdUseCase(ABC):
    """Represent an abstract base to retrieve a solve-job by its id."""

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(self, solve_job_id: str) -> SolveJob:
        """
        Represent an abstract base for callable objects to retrieve solve jobs.

        Parameters
        ----------
        solve_job_id : str
            The id of the solve-job to retrieve.
        """
