from typing import Literal

from pydantic import Field

from luna_quantum.solve.domain.abstract.luna_algorithm import LunaAlgorithm
from luna_quantum.solve.parameters.backends import FakeFujitsu


class FakeFujitsuDA(LunaAlgorithm[FakeFujitsu]):
    r"""
    Fake Fujitsu Digital Annealer Parameters.

    Parameters
    ----------
    scaling_action: Literal["NOTHING", "SCALING", "AUTO_SCALING"]
        Method for scaling ``qubo`` and determining temperatures:
        - "NOTHING": No action (use parameters exactly as specified)
        - "SCALING": ``scaling_factor`` is multiplied to ``qubo``,
          ``temperature_start``, ``temperature_end`` and ``offset_increase_rate``.
        - "AUTO_SCALING": A maximum scaling factor w.r.t. ``scaling_bit_precision``
          is multiplied to ``qubo``, ``temperature_start``, ``temperature_end`` and
          ``offset_increase_rate``.
    scaling_factor: int | float
        Multiplicative factor applied to model coefficients, temperatures, and other
        parameters: the ``scaling_factor`` for ``qubo``, ``temperature_start``,
        ``temperature_end`` and ``offset_increase_rate``.
        Higher values can improve numerical precision but may lead to overflow.
        Default is 1.0 (no scaling).
    scaling_bit_precision: int
        Maximum bit precision to use when scaling. Determines the maximum allowable
        coefficient magnitude. Default is 64, using full double precision.
    random_seed: Union[int, None]
        Seed for random number generation to ensure reproducible results.
        Must be between 0 and 9_999. Default is None (random seed).
    penalty_factor: float
        Penalty factor used to scale the equality constraint penalty function,
        default 1.0.
    inequality_factor: int
        Penalty factor used to scale the inequality constraints, default 1.
    remove_ohg_from_penalty: bool
        If equality constraints, identified to be One-Hot constraints are only
        considered within one-hot groups (`remove_ohg_from_penalty=True`), i.e.,
        identified one-hot constraints are not added to the penalty function,
        default True.
    optimization_method: Literal["annealing", "parallel_tempering"]
        Algorithm to use for optimization:
        - "annealing": Standard simulated annealing with gradual cooling
        - "parallel_tempering": Simultaneous runs at different temperatures with
          periodic state exchanges, effective for complex energy landscapes
        Default is "annealing".
    number_runs: int
        Number of stochastically independent runs. Default: 2, Min: 1, Max: 128
    number_replicas:
        Number of replicas in parallel tempering. Default: 5, Min: 5, Max: 128
    number_iterations: int
        Total number of iterations per run. Default: 1_000, Min: 1, Max: 100_000_000
    temperature_sampling: bool
        Temperatures. Default: True
    temperature_start: float
        Initial temperature for the annealing process. Higher values enable more
        exploration initially. Default is 1000.0. Range: [0.0, 1e20].
    temperature_end: float
        Final temperature for the annealing process. Lower values enforce more
        exploitation in final phases. Default is 1.0. Range: [0.0, 1e20].
    temperature_mode: int
        Cooling curve mode for temperature decay:
        - 0: Exponential cooling - Reduce temperature by factor
             :math:`(1-temperature\\_decay)` every ``temperature_interval`` steps
        - 1: Inverse cooling - Reduce temperature by factor
             :math:`(1-temperature\\_decay*temperature)` every `temperature_interval`
             steps
        - 2: Inverse root cooling - Reduce temperature by factor
             :math:`(1-temperature\\_decay*temperature^2)` every `temperature_interval`
             steps.
        Default is 0 (exponential).
    temperature_interval: int
        Number of iterations between temperature adjustments. Larger values
        allow more exploration at each temperature. Default is 1. Range: [1, 1e20].
    offset_increase_rate: float
        Rate at which dynamic offset increases when no bit is selected.
        Set to 0.0 to switch off dynamic energy feature.
        Helps escape plateaus in the energy landscape. Default is 5.0.
        Range: [0.0, 1e20].
    pt_temperature_model: Literal['Linear', 'Exponential', 'Hukushima']
        Temperature model for furnace temperature distribution for parallel tempering
        process. Default: 'Exponential'
    pt_replica_exchange_model: Literal['Neighbours', 'Far jump']
        Select replica exchange model for parallel tempering process.
        Default: "Neighbours"
    solution_mode: Literal["QUICK", "COMPLETE"]
        Determines solution reporting strategy:
        - "QUICK": Return only the overall best solution (faster)
        - "COMPLETE": Return best solutions from all runs (more diverse)
        Default is "COMPLETE", providing more solution options.
    scaling_action: Literal["NOTHING", "SCALING", "AUTO_SCALING"]
        Method for scaling ``qubo`` and determining temperatures:
        - "NOTHING": No action (use parameters exactly as specified)
        - "SCALING": ``scaling_factor`` is multiplied to ``qubo``,
          ``temperature_start``, ``temperature_end`` and ``offset_increase_rate``.
        - "AUTO_SCALING": A maximum scaling factor w.r.t. ``scaling_bit_precision``
          is multiplied to ``qubo``, ``temperature_start``, ``temperature_end`` and
          ``offset_increase_rate``.
    scaling_factor: int | float
        Multiplicative factor applied to model coefficients, temperatures, and other
        parameters: the ``scaling_factor`` for ``qubo``, ``temperature_start``,
        ``temperature_end`` and ``offset_increase_rate``.
        Higher values can improve numerical precision but may lead to overflow.
        Default is 1.0 (no scaling).
    scaling_bit_precision: int
        Maximum bit precision to use when scaling. Determines the maximum allowable
        coefficient magnitude. Default is 64, using full double precision.
    guidance_config: PartialConfig | None
        Specifies an initial value for each polynomial (problem) variable that is
        set to find an optimal solution. By specifying a value that is close to the
        optimal solution, improvement in the accuracy of the optimal solution can be
        expected. If you repeatedly use the specified initial values to solve the
        same polynomial (problem), the same optimal solution is obtained each time.
    random_seed: Union[int, None]
        Seed for random number generation to ensure reproducible results.
        Must be between 0 and 9_999. Default is None (random seed).
    inequality_factor: int
        Penalty factor used to scale the inequality constraints, default 1.
    remove_ohg_from_penalty: bool
        If equality constraints, identified to be One-Hot constraints are only
        considered within one-hot groups (`remove_ohg_from_penalty=True`), i.e.,
        identified one-hot constraints are not added to the penalty function,
        default True.
    """

    scaling_action: Literal["NOTHING", "SCALING", "AUTO_SCALING"] = "NOTHING"
    scaling_factor: int | float = 1.0
    scaling_bit_precision: int = 64
    random_seed: int | None = Field(default=None, ge=0, le=9_999)

    penalty_factor: float = 1.0
    inequality_factor: int = 1
    remove_ohg_from_penalty: bool = True

    optimization_method: Literal["annealing", "parallel_tempering"] = "annealing"

    number_runs: int = Field(default=2, ge=1, le=128)
    number_replicas: int = Field(default=5, ge=5, le=128)
    number_iterations: int = Field(default=1_000, ge=1, le=100_000_000)
    temperature_sampling: bool = True
    temperature_start: float = Field(default=1_000.0, ge=0.0, le=1e20)
    temperature_end: float = Field(default=1.0, ge=0.0, le=1e20)
    temperature_mode: int = 0
    temperature_interval: int = Field(default=1, ge=1, le=int(1e20))
    offset_increase_rate: float = Field(default=5.0, ge=0.0, le=1e20)
    pt_temperature_model: Literal["Linear", "Exponential", "Hukushima"] = "Exponential"
    pt_replica_exchange_model: Literal["Neighbours", "Far jump"] = "Neighbours"
    solution_mode: Literal["QUICK", "COMPLETE"] = "COMPLETE"

    @classmethod
    def get_default_backend(cls) -> FakeFujitsu:
        """
        Return the default backend implementation.

        This property must be implemented by subclasses to provide
        the default backend instance to use when no specific backend
        is specified.

        Returns
        -------
            IBackend
                An instance of a class implementing the IBackend interface that serves
                as the default backend.
        """
        return FakeFujitsu()

    @classmethod
    def get_compatible_backends(cls) -> tuple[type[FakeFujitsu], ...]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """
        return (FakeFujitsu,)

    @property
    def algorithm_name(self) -> str:
        """
        Returns the name of the algorithm.

        This abstract property method is intended to be overridden by subclasses.
        It should provide the name of the algorithm being implemented.

        Returns
        -------
        str
            The name of the algorithm.
        """
        return "FFDA"
