from typing import Literal

from pydantic import BaseModel, Field, PositiveInt


class CustomConfig(BaseModel):
    """Additional FlexQAOA circuit configuration.

    Attributes
    ----------
    max_qubits : PositiveInt | None
        Maximum number of qubits allowed for the circuit. If `None`, no limit is
        applied. Default: `None`.
    minimize_qubits : bool
        Minimize the number of used qubits in the circuit if set to `True`. Otherwise,
        minimize circuit depth. Default: `False`.
    wstate : Literal["log", "bilinear", "linear"]
        WState generation cricuit. Choice between:

        - `"log"`: Logarithmic-depth binary tree circuit.
        - `"linear"`: Linear circuit construction.
        - `"bilinear"`: Bi-linear circuit construction, starts in the middle and
                        linearly constructs the circuit outwards.

        Default: `"log"`
    qft_synth : Literal["line", "full"]
        QFT synthesis method. Choice between:

        - `"full"`: Shorter circuit depth implementation that requires all-to-all
                    connectivity.
        - `"line"`: Longer circuit depth implementation that requires linear
                    connectivity.

        Default: `"full"`
    """

    max_qubits: PositiveInt | None = Field(
        default=None,
        description="Maximum number of qubits allowed for the circuit. If `None`, no "
        "limit is applied.",
    )
    minimize_qubits: bool = Field(
        default=False,
        description="Minimize the number of used qubits in the circuit "
        "if set to `True`. Otherwise, minimize circuit depth.",
    )
    wstate: Literal["log", "bilinear", "linear"] = Field(
        default="log",
        description="WState generation cricuit. Choice between: Logarithmic-depth (log)"
        " binary tree circuit and linear or bilinear construction. bilinear places the "
        "start in the middle and linearly constructs the circuit outwards.",
    )
    qft_synth: Literal["line", "full"] = Field(
        default="full",
        description="QFT synthesis method. Shorter depth (full) implementation requires"
        " all-to-all connectivity. Longer (line) implementation requires only linear "
        "connectivity.",
    )
