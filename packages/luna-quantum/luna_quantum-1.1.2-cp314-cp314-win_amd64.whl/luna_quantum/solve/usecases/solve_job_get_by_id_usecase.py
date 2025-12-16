from typing import TYPE_CHECKING

from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.solve.domain.solve_job import SolveJob
from luna_quantum.solve.interfaces.usecases.solve_job_get_by_id_usecase_i import (
    ISolveJobGetByIdUseCase,
)
from luna_quantum.util.log_utils import Logging, progress

if TYPE_CHECKING:
    from luna_quantum.client.schemas.solve_job import SolveJobSchema


class SolveJobGetByIdUseCase(ISolveJobGetByIdUseCase):
    """
    Represent an abstract base to retrieve a solve-job by its id.

    This class interacts with a backend client to retrieve a solve job by its id.

    Attributes
    ----------
    client : ILunaSolve
        Client used to retrieve the solve job.
    """

    client: ILunaSolve
    logger = Logging.get_logger(__name__)

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Retrieving solve job by id...")
    def __call__(self, solve_job_id: str) -> SolveJob:
        """
        Retive a solve-job by its id.

        Parameters
        ----------
        solve_job_id : str
            The id of the solve-job to retrieve.
        """
        solve_job: SolveJobSchema = self.client.solve_job.get(solve_job_id=solve_job_id)

        return SolveJob.model_validate(solve_job.model_dump())
