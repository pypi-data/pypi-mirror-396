"""Profilers for multiple languages.

Currently supports Python. Extensible for future language support via the
generic Profiler base class and detector system.
"""

from .base import Profiler
from .python.scalene_profiler import ScaleneProfiler

__all__ = [
    "Profiler",
    "ScaleneProfiler",
]
