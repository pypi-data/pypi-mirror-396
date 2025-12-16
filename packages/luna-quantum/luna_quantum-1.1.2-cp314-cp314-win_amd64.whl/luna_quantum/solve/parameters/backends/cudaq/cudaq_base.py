from typing import Any

from pydantic import SerializationInfo, SerializerFunctionWrapHandler, model_serializer

from luna_quantum.solve.interfaces.backend_i import IBackend


class BaseCudaqBackend(IBackend):
    """CudaQBackend."""

    @model_serializer(mode="wrap")
    def _serialize(
        self, serializer: SerializerFunctionWrapHandler, _: SerializationInfo
    ) -> dict[str, dict[str, Any]]:
        data = serializer(self)
        return {"backend": data}
