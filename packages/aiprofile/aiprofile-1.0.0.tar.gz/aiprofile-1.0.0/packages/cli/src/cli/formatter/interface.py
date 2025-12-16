"""Abstract interface for output formatters."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class IFormatter(ABC):
    """Interface for output formatters."""

    @abstractmethod
    def print_header(self, title: str) -> None:
        """Print a header banner."""
        pass

    @abstractmethod
    def print_cpu_profile(self, cpu_profile: dict[str, Any]) -> None:
        """Print CPU profiling results."""
        pass

    @abstractmethod
    def print_memory_profile(self, memory_profile: dict[str, Any]) -> None:
        """Print memory profiling results."""
        pass

    @abstractmethod
    def print_analysis_result(self, analysis: dict[str, Any]) -> None:
        """Print AI analysis results."""
        pass

    @abstractmethod
    def print_error(self, message: str, error: Optional[Exception] = None) -> None:
        """Print an error message."""
        pass

    @abstractmethod
    def print_success(self, message: str) -> None:
        """Print a success message."""
        pass
