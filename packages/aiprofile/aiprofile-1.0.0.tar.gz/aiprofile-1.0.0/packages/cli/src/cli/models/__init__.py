"""Data models for AI Profiler."""

from .analysis import AnalysisResult, Bottleneck, Suggestion
from .profiling import (
    CPUProfile,
    FunctionProfile,
    MemoryAllocator,
    MemoryProfile,
    ProfilingResult,
    PythonCPUProfile,
    PythonFunctionProfile,
    PythonMemoryAllocator,
    PythonMemoryProfile,
    PythonProfilingResult,
)

__all__ = [
    # Generic base models
    "ProfilingResult",
    "CPUProfile",
    "MemoryProfile",
    "FunctionProfile",
    "MemoryAllocator",
    # Python-specific models
    "PythonProfilingResult",
    "PythonCPUProfile",
    "PythonMemoryProfile",
    "PythonFunctionProfile",
    "PythonMemoryAllocator",
    # Analysis models
    "AnalysisResult",
    "Bottleneck",
    "Suggestion",
]
