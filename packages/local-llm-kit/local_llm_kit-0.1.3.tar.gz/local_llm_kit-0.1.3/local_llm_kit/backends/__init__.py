"""
Model backends for inference.
"""
from typing import TYPE_CHECKING

from .base import BaseBackend

if TYPE_CHECKING:  # pragma: no cover - import-time convenience for type checkers
    from .transformers import TransformersBackend
    from .llamacpp import LlamaCppBackend

__all__ = ["BaseBackend", "TransformersBackend", "LlamaCppBackend"]


def __getattr__(name):
    if name == "TransformersBackend":
        from .transformers import TransformersBackend

        return TransformersBackend
    if name == "LlamaCppBackend":
        from .llamacpp import LlamaCppBackend

        return LlamaCppBackend
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
