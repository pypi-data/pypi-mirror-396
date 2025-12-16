from typing import Literal

from luna_quantum.solve.parameters.backends.cudaq.cudaq_base import BaseCudaqBackend


class CudaqGpu(BaseCudaqBackend):
    """CUDA-Q GPU Simulator.

    Use a NVIDIA CUDA-Q GPU simulator for circuit execution on Aqarios servers.

    You have the choice between the statevector simulator `"nvidia"`, and two tensor
    network based simulators `"tensornet"` and `"tensornet-mps"`.
    The floating point precision can be increased by setting `option` to `"fp64"`.

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
        return "cudaq-gpu"

    target: Literal["nvidia", "tensornet", "tensornet-mps"] = "nvidia"
    option: Literal["fp64", "fp32"] = "fp32"
