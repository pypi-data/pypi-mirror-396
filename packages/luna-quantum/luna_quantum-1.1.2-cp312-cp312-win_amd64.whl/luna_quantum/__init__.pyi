from warnings import deprecated
from ._core import (
    Bounds,
    Comparator,
    Constant,
    Constraint,
    ConstraintCollection,
    ConstraintType,
    Environment,
    Expression,
    ExpressionIterator,
    HigherOrder,
    Linear,
    ModelSpecs,
    Quadratic,
    Result,
    ResultIterator,
    ResultView,
    Sample,
    SampleIterator,
    Samples,
    SamplesIterator,
    Sense,
    Solution,
    Timer,
    Timing,
    Unbounded,
    Variable,
    ValueSource,
    Vtype,
    errors,
    transformations,
    translator,
    utils,
)
from .utils import quicksum
from luna_quantum._core import __luna_quantum_version__
from luna_quantum.aqm_overwrites.model import Model
from luna_quantum.client.controllers import LunaQ, LunaSolve
from luna_quantum.config import config
from luna_quantum.solve import DefaultToken
from luna_quantum.solve.parameters import algorithms, backends, constants
from luna_quantum.util.debug_info import debug_info
from luna_quantum.util.log_utils import Logging

@deprecated(
    "`Constraints` class name is deprecated and will be removed, use `ConstraintCollection` instead."
)
class Constraints(ConstraintCollection): ...

__version__ = __luna_quantum_version__
__all__ = [
    "Bounds",
    "Comparator",
    "Constant",
    "Constraint",
    "ConstraintCollection",
    "ConstraintType",
    "Constraints",
    "DefaultToken",
    "Environment",
    "Expression",
    "ExpressionIterator",
    "HigherOrder",
    "Linear",
    "Logging",
    "LunaQ",
    "LunaSolve",
    "Model",
    "ModelSpecs",
    "Quadratic",
    "Result",
    "ResultIterator",
    "ResultView",
    "Sample",
    "SampleIterator",
    "Samples",
    "SamplesIterator",
    "Sense",
    "Solution",
    "Timer",
    "Timing",
    "Unbounded",
    "ValueSource",
    "Variable",
    "Vtype",
    "__version__",
    "algorithms",
    "backends",
    "config",
    "constants",
    "debug_info",
    "errors",
    "quicksum",
    "transformations",
    "translator",
    "utils",
]
