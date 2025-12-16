from luna_quantum.solve.errors.solve_base_error import SolveBaseError


class QAOAParameterOptimizerError(SolveBaseError):
    """QAOA cirucit parameters mismatch with optimizer exception."""

    def __init__(
        self,
        optimizer: str,
        params: str,
        extra: str = "",
    ) -> None:
        super().__init__(
            f"Parameter Mismatch of '{optimizer}' and '{params}'"
            + ((": " + extra) if extra else ".")
        )


class InterpolateOptimizerError(SolveBaseError):
    """Interpolate optimizer error when final number of reps is too small."""

    def __init__(self, reps_end: int, reps_start: int) -> None:
        super().__init__(f"{reps_end=} needs to be larger than {reps_start=}.")


class QAOAParameterRepsMismatchError(SolveBaseError):
    """QAOA circuit params mismatch the specified reps."""

    def __init__(self, params_reps: int, reps: int) -> None:
        super().__init__(f"{params_reps=} needs to match {reps=}.")
