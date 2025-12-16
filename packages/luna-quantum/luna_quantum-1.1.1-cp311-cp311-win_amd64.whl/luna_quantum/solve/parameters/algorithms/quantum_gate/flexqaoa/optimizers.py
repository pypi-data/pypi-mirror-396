from typing import Literal

from pydantic import BaseModel, Field

from luna_quantum.solve.parameters.algorithms.base_params.scipy_optimizer import (
    ScipyOptimizerParams,
)


class CombinedOptimizerParams(BaseModel):
    """Combination of LinearOptimizer and ScipyOptimizer.

    Optimizer that first performs an optimization of the linear schedule and then
    fine tunes individual parameters. Only works in conjunction with `LinearQAOAParams`.


    Attributes
    ----------
    linear: ScipyOptimizerParams
        Parameters of the linear optimizer.
    fine_tune: ScipyOptimizerParams | None
        Parameters of the fine tuning optimizer. If `None`, the same optimizer is used.
        Default: `None`.
    """

    optimizer_type: Literal["combined"] = "combined"
    linear: ScipyOptimizerParams = Field(default_factory=lambda: ScipyOptimizerParams())
    fine_tune: ScipyOptimizerParams | None = None


class InterpolateOptimizerParams(BaseModel):
    """Optimizer with sequentially increasing number of QAOA layers.

    Optimizer that starts with `reps` iteration and interpolates sequentially in
    `reps_step` steps to `reps_end`. In between it performs a full optimization routine
    tunes individual parameters.

    Attributes
    ----------
    optimizer: ScipyOptimizerParams
        Parameters of the optimizer.
    reps_step: int
        Number of QAOA layers added for one interpolation.
    reps_end: int
        Final number of QAOA layers to be reached.
    """

    optimizer_type: Literal["interpolate"] = "interpolate"
    optimizer: ScipyOptimizerParams = Field(
        default_factory=lambda: ScipyOptimizerParams()
    )
    reps_step: int = Field(default=1, ge=1)
    reps_end: int = Field(default=10, ge=1, lt=1000)
