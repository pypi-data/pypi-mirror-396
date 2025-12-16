from luna_quantum.client.schemas.enums.call_style import CallStyle
from luna_quantum.exceptions.base_luna_quantum_error import BaseLunaQuantumError


class LunaQuantumCallStyleError(BaseLunaQuantumError):
    """Luna Quantum call style error."""

    def __init__(self, call_style: CallStyle) -> None:
        super().__init__(f"The call style '{call_style}' is not supported.")
