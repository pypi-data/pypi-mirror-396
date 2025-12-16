"""Emotion Machine Python SDK."""

from importlib import metadata

from .client import EmotionMachine, APIError
from .resources.knowledge import KnowledgeJobFailed

try:
    __version__ = metadata.version("emotion-machine")
except metadata.PackageNotFoundError:  # pragma: no cover - local dev fallback
    __version__ = "0.0.0"

__all__ = ["EmotionMachine", "APIError", "KnowledgeJobFailed", "__version__"]
