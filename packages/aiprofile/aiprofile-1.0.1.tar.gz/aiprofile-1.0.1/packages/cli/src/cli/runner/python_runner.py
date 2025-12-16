"""Python script runner using subprocess for safe execution."""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from cli.core import (
    ScriptNotFoundError,
    ScriptSyntaxError,
)

from .base import ScriptRunner
from .models import ExecutionConfig, ExecutionResult


class PythonScriptRunner(ScriptRunner):
    """Runner for executing Python scripts safely using subprocess."""

    DEFAULT_TIMEOUT = 300  # 5 minutes
    DEFAULT_MEMORY_LIMIT_MB = 4096  # 4GB

    def __init__(self, timeout_seconds: Optional[int] = None):
        """
        Initialize the Python runner.

        Args:
            timeout_seconds: Default timeout for script execution
        """
        self.timeout_seconds = timeout_seconds or self.DEFAULT_TIMEOUT

    def run(
        self,
        script_path: str,
        script_args: Optional[list[str]] = None,
        config: Optional[ExecutionConfig] = None,
    ) -> ExecutionResult:
        """
        Execute a Python script safely using subprocess.

        Args:
            script_path: Path to the Python script
            script_args: Arguments to pass to the script
            config: Execution configuration

        Returns:
            ExecutionResult with execution details

        Raises:
            ScriptNotFoundError: If script file doesn't exist
            ScriptSyntaxError: If script has syntax errors
            TimeoutError: If execution exceeds timeout
            MemoryLimitError: If memory limit is exceeded
            ExecutionError: For other execution errors
        """
        script_args = script_args or []
        config = config or ExecutionConfig()

        # Validate script exists
        script_path_obj = self.validate_script_path(script_path)

        # Check for syntax errors
        self._check_syntax(script_path)

        # Prepare execution
        start_time = time.time()
        try:
            # Build command
            cmd = [sys.executable, str(script_path_obj)] + script_args

            # Get environment
            env = self._prepare_environment(config)

            # Execute script
            result = subprocess.run(
                cmd,
                timeout=config.duration_seconds,
                capture_output=config.capture_output,
                text=True,
                cwd=config.working_directory or None,
                env=env,
            )

            duration = time.time() - start_time

            return ExecutionResult(
                script_path=script_path,
                script_args=script_args,
                exit_code=result.returncode,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                duration_seconds=round(duration, 2),
                success=result.returncode == 0,
                error_message=None if result.returncode == 0 else "Script exited with error",
                timeout_exceeded=False,
                memory_limit_exceeded=False,
            )

        except subprocess.TimeoutExpired as e:
            duration = time.time() - start_time
            return ExecutionResult(
                script_path=script_path,
                script_args=script_args,
                exit_code=-1,
                stdout=e.stdout or "",
                stderr=e.stderr or "",
                duration_seconds=round(duration, 2),
                success=False,
                error_type="TimeoutError",
                error_message=f"Script execution timed out after {config.duration_seconds} seconds",
                timeout_exceeded=True,
                memory_limit_exceeded=False,
            )

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            return ExecutionResult(
                script_path=script_path,
                script_args=script_args,
                exit_code=e.returncode,
                stdout=e.stdout or "",
                stderr=e.stderr or "",
                duration_seconds=round(duration, 2),
                success=False,
                error_type="ExecutionError",
                error_message=f"Script failed with exit code {e.returncode}",
                timeout_exceeded=False,
                memory_limit_exceeded=False,
            )

        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                script_path=script_path,
                script_args=script_args,
                exit_code=-1,
                duration_seconds=round(duration, 2),
                success=False,
                error_type=type(e).__name__,
                error_message=str(e),
                timeout_exceeded=False,
                memory_limit_exceeded=False,
            )

    def validate_script_path(self, script_path: str) -> Path:
        """
        Validate that script path exists and is readable.

        Args:
            script_path: Path to validate

        Returns:
            Resolved Path object

        Raises:
            ScriptNotFoundError: If script doesn't exist or isn't readable
        """
        try:
            path = Path(script_path).resolve()

            if not path.exists():
                raise ScriptNotFoundError(f"Script file not found: {script_path}")

            if not path.is_file():
                raise ScriptNotFoundError(f"Not a file: {script_path}")

            if not os.access(path, os.R_OK):
                raise ScriptNotFoundError(f"Script is not readable: {script_path}")

            return path

        except OSError as e:
            raise ScriptNotFoundError(f"Error accessing script: {e}") from e

    def validate_script(self, script_path: str) -> bool:
        """
        Check if script can be executed.

        Args:
            script_path: Path to the script

        Returns:
            True if valid, False otherwise
        """
        try:
            self.validate_script_path(script_path)
            self._check_syntax(script_path)
            return True
        except (ScriptNotFoundError, ScriptSyntaxError):
            return False

    def _check_syntax(self, script_path: str) -> None:
        """
        Check script for syntax errors.

        Args:
            script_path: Path to the script

        Raises:
            ScriptSyntaxError: If syntax is invalid
        """
        try:
            with open(script_path, encoding="utf-8") as f:
                code = f.read()

            compile(code, script_path, "exec")

        except SyntaxError as e:
            raise ScriptSyntaxError(
                f"Syntax error in {script_path} at line {e.lineno}: {e.msg}"
            ) from e
        except Exception as e:
            raise ScriptSyntaxError(f"Error checking syntax: {e}") from e

    def _prepare_environment(self, config: ExecutionConfig) -> Optional[dict[str, str]]:
        """
        Prepare environment for script execution.

        Args:
            config: Execution configuration

        Returns:
            Environment dictionary or None
        """
        if config.inherit_env:
            return os.environ.copy()
        return None

    def get_language(self) -> str:
        """Get the language this runner supports."""
        return "python"

    def supports_language(self, language: str) -> bool:
        """Check if this runner supports a language."""
        return language.lower() in ("python", "py", "python3")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"PythonScriptRunner(timeout={self.timeout_seconds}s, "
            f"memory_limit={self.DEFAULT_MEMORY_LIMIT_MB}MB)"
        )
