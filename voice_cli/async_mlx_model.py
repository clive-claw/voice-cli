"""Generic async wrapper for MLX (and similar) synchronous models.

Encapsulates the lazy-load + asyncio-executor + import-fallback lifecycle that
both stt.py and tts.py share.  Model-specific callers configure an instance
with a *loader* callable (returns the model or None on failure) and a *transform*
callable (takes ``(model, input)`` and returns the output).
"""

import asyncio
from typing import Any, Callable, Generic, Optional, TypeVar

T_in = TypeVar("T_in")
T_out = TypeVar("T_out")


class AsyncMLXModel(Generic[T_in, T_out]):
    """Lazy-load a synchronous model and run its transform in an executor.

    Parameters
    ----------
    loader:
        Zero-argument callable that loads the model synchronously and returns it,
        or returns ``None`` (or raises) if the model is unavailable.
    transform:
        Two-argument callable ``(model, input) -> output`` that runs the model
        synchronously.  It may raise; the caller is responsible for catching.
    """

    def __init__(
        self,
        loader: Callable[[], Any],
        transform: Callable[[Any, T_in], T_out],
    ) -> None:
        self._loader = loader
        self._transform = transform
        self._model: Optional[Any] = None

    async def initialize(self) -> None:
        """Load the model in the default executor (non-blocking)."""
        loop = asyncio.get_event_loop()
        try:
            self._model = await loop.run_in_executor(None, self._loader)
        except Exception:
            self._model = None

    async def run(self, input: T_in) -> T_out:
        """Run the transform in the default executor.

        Raises
        ------
        RuntimeError
            If the model was not loaded (``initialize()`` was not called or the
            loader returned ``None``), or if the transform itself raises.
        """
        if self._model is None:
            raise RuntimeError("Model not available")

        loop = asyncio.get_event_loop()

        def _call() -> T_out:
            return self._transform(self._model, input)

        return await loop.run_in_executor(None, _call)
