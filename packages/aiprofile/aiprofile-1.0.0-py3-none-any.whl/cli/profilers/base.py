"""Abstract base class for profilers."""

from abc import ABC, abstractmethod
from typing import Optional

from cli.models import ProfilingResult
from cli.runner import ExecutionConfig


class Profiler(ABC):
    """Abstract base class for language-specific profilers."""

    @abstractmethod
    def profile(
        self,
        script_path: str,
        script_args: Optional[list[str]] = None,
        config: Optional[ExecutionConfig] = None,
    ) -> ProfilingResult:
        """
        Profile a script and return results.

        Args:
            script_path: Path to script
            script_args: Script arguments
            config: Execution configuration

        Returns:
            ProfilingResult with profiling data
        """
        pass

    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """Check if this profiler supports a language."""
        pass

    @abstractmethod
    def get_language(self) -> str:
        """Get the language this profiler supports."""
        pass

    @abstractmethod
    def get_profiler_type(self) -> str:
        """Get the profiler type (scalene, cprofile, etc)."""
        pass

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(language={self.get_language()})"
