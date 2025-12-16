"""Custom exception types for the AI Profiler application."""


class AIProfilerError(Exception):
    """Base exception for all AI Profiler errors."""

    pass


class ExecutionError(AIProfilerError):
    """Raised when script execution fails."""

    pass


class TimeoutError(ExecutionError):
    """Raised when script execution times out."""

    pass


class MemoryLimitError(ExecutionError):
    """Raised when script exceeds memory limit."""

    pass


class ScriptNotFoundError(ExecutionError):
    """Raised when the script file is not found."""

    pass


class ScriptSyntaxError(ExecutionError):
    """Raised when the script has syntax errors."""

    pass


class ResourceLimitError(ExecutionError):
    """Raised when system resource limits are exceeded."""

    pass


class ProfilingError(AIProfilerError):
    """Raised when profiling fails."""

    pass


class ScaleneError(ProfilingError):
    """Raised when Scalene profiling fails."""

    pass


class ProfilerNotAvailableError(ProfilingError):
    """Raised when a profiler is not available for a language."""

    pass


class AnalysisError(AIProfilerError):
    """Raised when AI analysis fails."""

    pass


class ClaudeAPIError(AnalysisError):
    """Raised when Claude API call fails."""

    pass


class ResponseParsingError(AnalysisError):
    """Raised when Claude response cannot be parsed."""

    pass


class APIKeyNotFoundError(AnalysisError):
    """Raised when API key is not configured."""

    pass


class ConfigurationError(AIProfilerError):
    """Raised when configuration is invalid."""

    pass


class ValidationError(AIProfilerError):
    """Raised when validation fails."""

    pass


class UnsupportedLanguageError(ConfigurationError):
    """Raised when an unsupported language is specified."""

    pass
