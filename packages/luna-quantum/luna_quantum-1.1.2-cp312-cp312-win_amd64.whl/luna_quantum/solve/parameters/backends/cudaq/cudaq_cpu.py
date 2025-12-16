from typing import Literal

from .cudaq_base import BaseCudaqBackend


class CudaqCpu(BaseCudaqBackend):
    """CUDA-Q CPU Simulator.

    Use a NVIDIA CUDA-Q CPU simulator for circuit execution on Aqarios servers.

    You have the choice between the statevector simulator `"qpp-cpu"` and the density
    matrix based simulator `"density-matrix-cpu"`.

    For more information on the simulators pelase refer to the
    [CUDA-Q documentation.](https://nvidia.github.io/cuda-quantum/latest/using/backends/simulators.html)
    """

    @property
    def provider(self) -> str:
        """
        Retrieve the name of the provider.

        Returns
        -------
        str
            The name of the provider.
        """
        return "cudaq"

    target: Literal["qpp-cpu", "density-matrix-cpu"] = "qpp-cpu"
