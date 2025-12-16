"""Unified profiling result models for all languages."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FunctionProfile(BaseModel):
    """Generic function profile (language-agnostic base)."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Function name")
    file_path: str = Field(description="Path to file containing function")
    line_number: int = Field(description="Line number where function is defined")
    cpu_percent: float = Field(description="CPU time percentage", ge=0, le=100)
    cpu_seconds: float = Field(description="CPU time in seconds", ge=0)
    memory_mb: float = Field(description="Peak memory usage in MB", ge=0, default=0)
    call_count: Optional[int] = Field(
        description="Number of times function was called (None if not available from profiler)",
        ge=0,
        default=None,
    )


class PythonFunctionProfile(FunctionProfile):
    """Python-specific function profile with runtime metrics."""

    model_config = ConfigDict(frozen=True)

    # CPU breakdown (Python-specific: bytecode vs C extensions vs syscalls)
    # These represent portions of cpu_percent, should sum to <= cpu_percent
    python_cpu_percent: float = Field(
        description="Python bytecode/interpreter CPU percentage (part of cpu_percent)",
        ge=0,
        le=100,
        default=0,
    )
    c_cpu_percent: float = Field(
        description="C extension/native code CPU percentage (part of cpu_percent)",
        ge=0,
        le=100,
        default=0,
    )
    sys_percent: float = Field(
        description="System call CPU percentage (part of cpu_percent)", ge=0, le=100, default=0
    )

    # Memory patterns
    memory_growth_mb: float = Field(
        description="Memory growth during function execution", ge=0, default=0
    )
    memory_avg_mb: float = Field(description="Average memory during execution", ge=0, default=0)

    # Performance metrics
    core_utilization: float = Field(
        description="CPU core utilization ratio (0-1)", ge=0, le=1, default=0
    )
    copy_mb_s: float = Field(description="Memory copy bandwidth MB/s", ge=0, default=0)

    # GPU metrics (for ML workloads like TensorFlow, PyTorch)
    gpu_peak_memory_mb: float = Field(description="GPU peak memory in MB", ge=0, default=0)
    gpu_percent: float = Field(description="GPU utilization percentage", ge=0, le=100, default=0)

    @field_validator("python_cpu_percent", "c_cpu_percent", "sys_percent", mode="after")
    @classmethod
    def validate_breakdown_percentages(cls, v: float) -> float:
        """Ensure breakdown percentages don't exceed 100."""
        return min(100.0, max(0.0, v))


class CPUProfile(BaseModel):
    """Generic CPU profiling results (language-agnostic)."""

    model_config = ConfigDict(frozen=True)

    total_duration_seconds: float = Field(description="Total script execution duration", ge=0)
    top_functions: list[FunctionProfile] = Field(
        description="Top functions ranked by CPU consumption",
        default_factory=list,
        max_length=50,
    )


class PythonCPUProfile(CPUProfile):
    """Python-specific CPU profiling with runtime breakdown."""

    model_config = ConfigDict(frozen=True)

    top_functions: list[PythonFunctionProfile] = Field(
        description="Top Python functions ranked by CPU consumption",
        default_factory=list,
        max_length=50,
    )


class MemoryAllocator(BaseModel):
    """Generic memory allocator (language-agnostic base)."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Allocator/location name (e.g., function or line number)")
    file_path: str = Field(description="File path where allocation occurred")
    line_number: int = Field(description="Line number where allocation occurred (0 = file-level)")
    memory_mb: float = Field(description="Peak memory allocated in MB", ge=0)
    occurrences: int = Field(description="Number of allocation events", ge=0, default=1)


class PythonMemoryAllocator(MemoryAllocator):
    """Python-specific memory allocator with detailed breakdown."""

    model_config = ConfigDict(frozen=True)

    # Optional advanced metrics (Python-specific from Scalene)
    avg_memory_mb: float = Field(description="Average memory during execution", ge=0, default=0)
    growth_mb: float = Field(description="Net memory growth in MB", ge=0, default=0)
    malloc_count: int = Field(
        description="Number of allocation operations (malloc, new, etc.)",
        ge=0,
        default=0,
    )
    malloc_mb: float = Field(description="Total memory from allocations in MB", ge=0, default=0)
    copy_mb_s: float = Field(description="Memory copy/move bandwidth MB/s", ge=0, default=0)


class MemoryProfile(BaseModel):
    """Generic memory profiling results (language-agnostic)."""

    model_config = ConfigDict(frozen=True)

    peak_memory_mb: float = Field(description="Peak heap/managed memory during execution", ge=0)
    baseline_memory_mb: float = Field(description="Starting memory baseline in MB", ge=0)
    memory_growth_mb: float = Field(description="Net memory growth MB", ge=0)
    top_allocators: list[MemoryAllocator] = Field(
        description="Top memory hotspots ranked by consumption",
        default_factory=list,
        max_length=50,
    )


class PythonMemoryProfile(MemoryProfile):
    """Python-specific memory profiling with advanced metrics."""

    model_config = ConfigDict(frozen=True)

    top_allocators: list[PythonMemoryAllocator] = Field(
        description="Top Python memory hotspots ranked by consumption",
        default_factory=list,
        max_length=50,
    )


class ProfilingResult(BaseModel):
    """Generic profiling result (language-agnostic base)."""

    model_config = ConfigDict(frozen=True)

    script_path: str = Field(description="Path to profiled script/binary")
    script_args: list[str] = Field(
        description="Arguments passed to the script", default_factory=list
    )
    language: str = Field(
        description="Programming language (currently: python; future: go, rust, java, etc.)"
    )
    cpu_profile: CPUProfile = Field(description="CPU profiling data and hotspots")
    memory_profile: MemoryProfile = Field(description="Memory profiling data and allocators")
    success: bool = Field(description="Whether profiling succeeded")
    error_message: Optional[str] = Field(
        description="Error message if profiling failed", default=None
    )
    profiler_type: str = Field(description="Profiler type (scalene, cprofile, perf, nodejs, etc.)")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert to JSON."""
        return self.model_dump_json(indent=2)


class PythonProfilingResult(ProfilingResult):
    """Python-specific profiling result with Python metrics."""

    model_config = ConfigDict(frozen=True)

    language: str = Field(default="python", description="Python programming language")
    cpu_profile: PythonCPUProfile = Field(description="Python CPU profiling data")
    memory_profile: PythonMemoryProfile = Field(description="Python memory profiling data")
