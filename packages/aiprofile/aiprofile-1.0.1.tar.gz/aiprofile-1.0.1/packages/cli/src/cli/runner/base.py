"""Abstract base class for script runners."""

from abc import ABC, abstractmethod
from typing import Optional

from .models import ExecutionConfig, ExecutionResult


class ScriptRunner(ABC):
    """Abstract base class for running scripts."""

    @abstractmethod
    def run(
        self,
        script_path: str,
        script_args: Optional[list[str]] = None,
        config: Optional[ExecutionConfig] = None,
    ) -> ExecutionResult:
        """
        Run a script and return execution result.

        Args:
            script_path: Path to the script to run
            script_args: Arguments to pass to the script
            config: Execution configuration

        Returns:
            ExecutionResult with execution details
        """
        pass

    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """
        Check if this runner supports a specific language.

        Args:
            language: Language identifier (e.g., 'python', 'node', 'go')

        Returns:
            True if language is supported
        """
        pass
