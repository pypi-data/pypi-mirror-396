from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from luna_quantum.solve.domain.abstract.luna_algorithm import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params.qaoa_circuit_params import (
    BasicQAOAParams,
    LinearQAOAParams,
    RandomQAOAParams,
)
from luna_quantum.solve.parameters.algorithms.base_params.scipy_optimizer import (
    ScipyOptimizerParams,
)
from luna_quantum.solve.parameters.backends.aqarios import Aqarios
from luna_quantum.solve.parameters.backends.aqarios_gpu import AqariosGpu
from luna_quantum.solve.parameters.errors import (
    InterpolateOptimizerError,
    QAOAParameterOptimizerError,
    QAOAParameterRepsMismatchError,
)

from .config import CustomConfig
from .optimizers import CombinedOptimizerParams, InterpolateOptimizerParams
from .pipeline import PipelineParams


class FlexQAOA(LunaAlgorithm[Aqarios | AqariosGpu], BaseModel):
    """The FlexQAOA algorithm for constrained quantum optimization.

    The FlexQAOA is an extension to the default QAOA with the capabilities to encode
    inequality constriants with indicator functions as well as one-hot constraints
    through XY-mixers. This algorithm will dynamically extract all constraints from the
    given constraint input optimization model, and construct an accoring QAOA circuit.
    Currently only simulation of the circuit is supported. But due to the constrained
    nature, the subspace of the Hilbertspace required for simulation is smaller,
    depending on the problem instance. This allows for simulation of problems with
    more qubits than ordinary state vector simulation allows. For now, the simulation
    size is limited to Hilbertspaces with less <= 2**18 dimensions.

    The FlexQAOA allows for a dynamic circuit construction depending on input paramters.
    Central to this is the pipeline parameter which allows for different configurations.

    For instance, if one likes to explore ordinary QUBO simulation with all constraints
    represented as quadratic penalties, the `xy_mixers` and `indicator_function` options
    need to be manually disabled
    ```
    pipeline.xy_mixer.enable = False
    pipeline.indicator_function.enable = False
    ```

    Following the standard protocol for QAOA, a classical optimizer is required that
    tunes the variational parameters of the circuit. Besides the classical
    `ScipyOptimizer` other optimizers are also featured, allowing for optimizing only a
    linear schedule, starting with optimizing for a linear schedule followed by
    individual parameter fine tuning, and interpolating between different QAOA circuit
    depts.

    Attributes
    ----------
    shots: int
        Number of sampled shots.
    reps: int
        Number of QAOA layer repetitions
    pipeline: PipelineParams
        The pipeline defines the selected features for QAOA circuit generation. By
        default, all supported features are enabled (one-hot constraints, inequality
        constraints and quadratic penalties).
    optimizer: ScipyOptimizerParams | CombinedOptimizerParams |\
        InterpolateOptimizerParams | None
        The classical optimizer for parameter tuning. Setting
        to `None` disables the optimization, leading to an evaluation of the initial
        parameters.
    initial_params: LinearQAOAParams | BasicQAOAParams | RandomQAOAParams | Dict
        Custom QAOA variational circuit parameters. By default linear
        increasing/decreasing parameters for the selected `reps` are generated.
    param_conversion: None | Literal["basic"] = "basic"
        Parameter conversion after initialization. This option set to `None` means the
        parameters, as specified are used. This parameter set to `"basic"` means the
        parameters are converted to basic parameters before optimization. This is useful
        if one only wants to optimize the linear schedule of parameters: Then the option
        `None` needs to be selected alongside LinearQAOAParams. This
        option is ignored when CombinedOptimizer is also selected.
    custom_config: CustomConfig
        Additional options for the FlexQAOA circuit.
    """

    shots: int = Field(
        default=1024, ge=1, lt=1 << 16, description="Number of sampled shots."
    )
    reps: int = Field(
        default=1, ge=1, lt=1000, description="Number of QAOA layer repetitions"
    )
    pipeline: PipelineParams = Field(
        default_factory=lambda: PipelineParams(),
        description="The pipeline defines the selected features for QAOA circuit "
        "generation. By default, all supported features are enabled "
        "(one-hot constraints, inequality constraints and quadratic penalties).",
    )
    optimizer: (
        ScipyOptimizerParams
        | CombinedOptimizerParams
        | InterpolateOptimizerParams
        | None
    ) = Field(
        default_factory=lambda: ScipyOptimizerParams(),
        description="The classical optimizer. Default: ScipyOptimizer",
    )
    initial_params: LinearQAOAParams | BasicQAOAParams | RandomQAOAParams = Field(
        default_factory=lambda: LinearQAOAParams(delta_beta=0.5, delta_gamma=0.5),
        description="Custom QAOA circuit parameters. By default linear "
        "increasing/decreasing parameters for the selected `reps` are generated.",
    )
    param_conversion: None | Literal["basic"] = "basic"
    custom_config: CustomConfig = Field(
        default_factory=lambda: CustomConfig(),
        description="Additional configuration options for the FlexQAOA circuit.",
    )

    @model_validator(mode="after")
    def _check_param_type(self) -> FlexQAOA:
        if isinstance(self.optimizer, CombinedOptimizerParams):
            if isinstance(self.initial_params, (BasicQAOAParams, RandomQAOAParams)):
                optim = self.optimizer.__class__.__name__
                params = self.initial_params.__class__.__name__
                raise QAOAParameterOptimizerError(optim, params)
            self.param_conversion = None
        if (
            isinstance(self.optimizer, InterpolateOptimizerParams)
            and self.optimizer.reps_end < self.reps
        ):
            raise InterpolateOptimizerError(self.optimizer.reps_end, self.reps)
        return self

    @model_validator(mode="after")
    def _check_depth(self) -> FlexQAOA:
        if (
            isinstance(self.initial_params, BasicQAOAParams)
            and self.initial_params.reps != self.reps
        ):
            raise QAOAParameterRepsMismatchError(self.initial_params.reps, self.reps)
        return self

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
        return "FlexQAOA"

    @classmethod
    def get_default_backend(cls) -> Aqarios:
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
        return Aqarios()

    @classmethod
    def get_compatible_backends(cls) -> tuple[type[Aqarios], type[AqariosGpu]]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """
        return (Aqarios, AqariosGpu)
