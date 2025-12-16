from luna_quantum.solve.interfaces.backend_i import IBackend


class AqariosGpu(IBackend):
    """Configuration class for the Aqarios GPU backend."""

    @property
    def provider(self) -> str:
        """
        Retrieve the name of the provider.

        Returns
        -------
        str
            The name of the provider.
        """
        return "aqarios-gpu"
