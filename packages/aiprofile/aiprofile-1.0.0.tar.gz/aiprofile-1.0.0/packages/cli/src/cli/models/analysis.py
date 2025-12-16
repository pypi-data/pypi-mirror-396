"""AI analysis result models."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class Suggestion(BaseModel):
    """Opt imization suggestion."""

    model_config = ConfigDict(frozen=True)

    description: str = Field(description="Detailed suggestion")
    estimated_improvement: str = Field(description="Expected improvement (e.g., '30-40% faster')")
    difficulty: str = Field(description="Implementation difficulty (Low/Medium/High)")


class Bottleneck(BaseModel):
    """Performance bottleneck."""

    model_config = ConfigDict(frozen=True)

    rank: int = Field(description="Rank by impact", ge=1, le=10)
    function_name: str = Field(description="Function name")
    file_path: str = Field(description="File path")
    line_number: Optional[int] = Field(description="Line number", default=None)
    impact_description: str = Field(description="What makes this a bottleneck")
    cpu_percent: Optional[float] = Field(description="CPU percentage", default=None, ge=0, le=100)
    memory_mb: Optional[float] = Field(description="Memory in MB", default=None, ge=0)
    suggestions: list[Suggestion] = Field(
        description="Optimization suggestions", default_factory=list
    )


class AnalysisResult(BaseModel):
    """AI analysis result from Claude."""

    model_config = ConfigDict(frozen=True)

    summary: str = Field(description="High-level summary of analysis")
    bottlenecks: list[Bottleneck] = Field(
        description="Top performance bottlenecks",
        default_factory=list,
        max_length=5,
    )
    general_recommendations: list[str] = Field(
        description="General optimization recommendations",
        default_factory=list,
    )
    raw_response: str = Field(description="Raw response from Claude", default="")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert to JSON."""
        return self.model_dump_json(indent=2)
