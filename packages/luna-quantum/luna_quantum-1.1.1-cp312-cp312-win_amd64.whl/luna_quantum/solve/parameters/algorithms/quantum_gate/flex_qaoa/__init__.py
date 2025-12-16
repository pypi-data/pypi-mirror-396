import warnings

from luna_quantum.solve.parameters.algorithms.quantum_gate.flexqaoa import *  # noqa: F403

warnings.warn(
    "The module `flex_qaoa` is deprecated and will be removed in the future. "
    "Use 'flexqaoa' instead.",
    DeprecationWarning,
    stacklevel=2,
)
