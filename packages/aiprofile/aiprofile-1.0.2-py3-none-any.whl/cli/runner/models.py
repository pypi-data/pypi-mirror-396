"""Pydantic models for script execution results."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExecutionResult(BaseModel):
    """Result of executing a Python script."""

    model_config = ConfigDict(frozen=True)

    script_path: str = Field(description="Path to the executed script")
    script_args: list[str] = Field(
        description="Arguments passed to the script", default_factory=list
    )
    exit_code: int = Field(description="Script exit code")
    stdout: str = Field(description="Standard output from script", default="")
    stderr: str = Field(description="Standard error from script", default="")
    duration_seconds: float = Field(description="Execution duration in seconds", ge=0)
    success: bool = Field(description="Whether script executed successfully")
    error_type: Optional[str] = Field(description="Type of error if execution failed", default=None)
    error_message: Optional[str] = Field(
        description="Error message if execution failed", default=None
    )
    timeout_exceeded: bool = Field(description="Whether execution timed out", default=False)
    memory_limit_exceeded: bool = Field(
        description="Whether memory limit was exceeded", default=False
    )

    def to_dict(self):
        """Convert to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=2)


class ExecutionConfig(BaseModel):
    """Configuration for script execution."""

    model_config = ConfigDict(frozen=True)

    duration_seconds: Optional[int] = Field(
        description="Maximum profiling duration in seconds (None for unlimited)", default=None, ge=1
    )
    memory_limit_mb: Optional[int] = Field(
        description="Memory limit in MB (None for unlimited)", default=None, ge=1
    )
    working_directory: Optional[str] = Field(
        description="Working directory for execution", default=None
    )
    capture_output: bool = Field(description="Whether to capture stdout/stderr", default=True)
    inherit_env: bool = Field(
        description="Whether to inherit parent process environment", default=True
    )
