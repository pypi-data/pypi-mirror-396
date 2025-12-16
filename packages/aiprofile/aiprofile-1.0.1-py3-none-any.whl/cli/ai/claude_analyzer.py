"""Claude AI analyzer using tool calling for structured output."""

import json
import os
import time
from typing import Any, Optional

from anthropic import Anthropic, APIConnectionError, APIError, RateLimitError

from cli.core import APIKeyNotFoundError, ClaudeAPIError, ResponseParsingError
from cli.models import AnalysisResult, Bottleneck, Suggestion


class ClaudeAnalyzer:
    """AI analyzer using Claude Haiku with tool calling for structured output."""

    MODEL = "claude-haiku-4-5-20251001"
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    MAX_TOKENS = 4096

    SYSTEM_PROMPT = (
        "You are an expert performance engineer analyzing profiling results. "
        "Analyze each function separately using source code and metrics provided. "
        "For each bottleneck: identify WHY it's a bottleneck (algorithmic complexity, "
        "I/O, data structure, memory allocation), suggest concrete optimizations with "
        "estimated impact, focus on different functions, consider BOTH CPU and memory "
        "metrics. Be technical, reference line numbers and code patterns. "
        "IMPORTANT: "
        "1. The summary must be CONCISE (1-2 sentences max, under 100 words). "
        "   Make it punchy and actionable, not verbose. "
        "2. In general_recommendations, provide ONLY 2-3 of the MOST CRITICAL "
        "   and ACTIONABLE recommendations. "
        "3. Focus on immediate high-impact improvements, not nice-to-have suggestions. "
        "Use provide_analysis tool to return structured analysis."
    )

    # Tool definition for structured output
    ANALYSIS_TOOL = {
        "name": "provide_analysis",
        "description": "Provide structured performance analysis results",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": (
                        "CONCISE 1-2 sentence summary (under 100 words). "
                        "Be punchy and actionable. Highlight the main issue and potential impact. "
                        "Example: 'O(n²) nested loops consume 45% CPU time. "
                        "Vectorization could reduce runtime by 50-60%.'"
                    ),
                },
                "bottlenecks": {
                    "type": "array",
                    "description": "Top 3-5 performance bottlenecks",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rank": {
                                "type": "integer",
                                "description": "Rank by impact (1-10)",
                            },
                            "function_name": {
                                "type": "string",
                                "description": "Function name",
                            },
                            "file_path": {
                                "type": "string",
                                "description": "File path",
                            },
                            "line_number": {
                                "type": ["integer", "null"],
                                "description": "Line number in the file",
                            },
                            "impact_description": {
                                "type": "string",
                                "description": "What makes this a bottleneck",
                            },
                            "cpu_percent": {
                                "type": ["number", "null"],
                                "description": "CPU percentage (0-100)",
                            },
                            "memory_mb": {
                                "type": ["number", "null"],
                                "description": "Memory usage in MB",
                            },
                            "suggestions": {
                                "type": "array",
                                "description": "Optimization suggestions",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "description": {
                                            "type": "string",
                                            "description": "Detailed suggestion",
                                        },
                                        "estimated_improvement": {
                                            "type": "string",
                                            "description": "Expected improvement",
                                        },
                                        "difficulty": {
                                            "type": "string",
                                            "description": "Implementation difficulty",
                                            "enum": ["Low", "Medium", "High"],
                                        },
                                    },
                                    "required": [
                                        "description",
                                        "estimated_improvement",
                                        "difficulty",
                                    ],
                                },
                            },
                        },
                        "required": [
                            "rank",
                            "function_name",
                            "file_path",
                            "impact_description",
                        ],
                    },
                    "maxItems": 5,
                },
                "general_recommendations": {
                    "type": "array",
                    "description": "General optimization recommendations",
                    "items": {"type": "string"},
                },
            },
            "required": ["summary", "bottlenecks", "general_recommendations"],
        },
    }

    def __init__(self, api_key: Optional[str] = None, include_source_code: bool = True):
        """
        Initialize Claude analyzer.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            include_source_code: Whether to extract and send source code (default True).
                Set to False for large projects to save context tokens.

        Raises:
            APIKeyNotFoundError: If API key not found
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise APIKeyNotFoundError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY "
                "environment variable or pass api_key parameter."
            )
        self.client = Anthropic(api_key=self.api_key)
        self.include_source_code = include_source_code

    def analyze(self, profiling_data: dict[str, Any]) -> AnalysisResult:
        """
        Analyze profiling data using Claude with retries.

        Args:
            profiling_data: Profiling result as dictionary

        Returns:
            AnalysisResult with AI insights

        Raises:
            ClaudeAPIError: If API calls fail after retries
            ResponseParsingError: If response cannot be parsed
        """
        analysis_payload = self._build_unified_payload(profiling_data)
        return self._call_claude_with_retries(analysis_payload)

    def _call_claude_with_retries(self, analysis_payload: dict[str, Any]) -> AnalysisResult:
        """
        Call Claude API with exponential backoff retry logic.

        Args:
            analysis_payload: Payload to send to Claude

        Returns:
            AnalysisResult with AI insights

        Raises:
            ClaudeAPIError: If API calls fail after retries
            ResponseParsingError: If response cannot be parsed
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self._send_to_claude(analysis_payload)
                return self._parse_response(response)

            except (RateLimitError, APIConnectionError) as e:
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY * (2**attempt)
                    time.sleep(delay)
                    continue
                msg = f"API error after {self.MAX_RETRIES} retries: {e}"
                raise ClaudeAPIError(msg) from e

            except APIError as e:
                raise ClaudeAPIError(f"Claude API error: {e}") from e

        # This should never be reached due to the raise in the loop
        raise ClaudeAPIError("Analysis failed after all retries")

    def _send_to_claude(self, analysis_payload: dict[str, Any]) -> Any:
        """
        Send profiling data to Claude API for analysis.

        Args:
            analysis_payload: Profiling data payload

        Returns:
            Response from Claude API
        """
        return self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            system=self.SYSTEM_PROMPT,
            tools=[self.ANALYSIS_TOOL],  # type: ignore[arg-type]
            tool_choice={"type": "tool", "name": "provide_analysis"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Analyze this profiling data:\n\n{json.dumps(analysis_payload, indent=2)}"
                    ),
                }
            ],
        )

    def _extract_source_code(
        self,
        file_path: str,
        line_number: Optional[int] = None,
        context_lines: int = 3,
        max_bytes: int = 1024,
    ) -> Optional[str]:
        """
        Extract minimal source code snippet for context-limited Claude.

        For large projects, prioritize: function signature, docstring, limited context,
        hard byte limit to prevent token bloat.

        Args:
            file_path: Path to source file
            line_number: Line to center on (None returns file preview)
            context_lines: Lines before/after target (reduced default)
            max_bytes: Maximum bytes to extract (prevents token bloat)

        Returns:
            Source code snippet or None if file not found
        """
        try:
            # Handle relative and absolute paths
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)

            if not os.path.exists(file_path):
                return None

            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if line_number is None:
                # Return just first 5 lines as preview
                return "".join(lines[:5])

            # Extract function definition and minimal context
            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)

            snippet_lines = []
            for i in range(start, end):
                line_num = i + 1
                marker = ">>>" if i == line_number - 1 else "   "
                line_text = lines[i].rstrip()
                snippet_lines.append(f"{marker} {line_num:4d}: {line_text}")

            snippet = "\n".join(snippet_lines)

            # Enforce byte limit to prevent token explosion
            if len(snippet.encode("utf-8")) > max_bytes:
                # Truncate intelligently: keep def line + marker line
                truncated = []
                for line in snippet_lines:
                    encoded_len = len("\n".join(truncated).encode("utf-8"))
                    if "def " in line or ">>>" in line or encoded_len < max_bytes // 2:
                        truncated.append(line)
                    else:
                        break
                truncated.append("    ... (truncated)")
                snippet = "\n".join(truncated)

            return snippet

        except OSError:
            return None

    def _build_unified_payload(self, profiling_data: dict[str, Any]) -> dict[str, Any]:
        """
        Build unified payload merging CPU and memory profiles.

        For large projects, only analyze top 5 functions to save context tokens.
        Both metrics are associated with the same function entry.
        """
        script_path = profiling_data.get("script_path", "unknown")
        cpu_profile = profiling_data.get("cpu_profile", {})
        memory_profile = profiling_data.get("memory_profile", {})

        # Build a map of functions from CPU profile
        # For large projects, only analyze top 5 functions
        functions_map: dict[tuple[str, int], dict[str, Any]] = {}

        top_functions = cpu_profile.get("top_functions", [])[:5]
        for func in top_functions:
            file_path = func.get("file_path", "unknown")
            line_num = func.get("line_number", 0)
            func_name = func.get("name", "unknown")

            key = (file_path, line_num)
            functions_map[key] = {
                "name": func_name,
                "file_path": file_path,
                "line_number": line_num,
                "cpu_percent": func.get("cpu_percent", 0),
                "cpu_seconds": func.get("cpu_seconds", 0),
                "cpu_call_count": func.get("call_count", 0),
                "memory_mb": None,
                "memory_call_count": None,
            }

        # Merge memory allocators (limit to top 5 to match CPU scope)
        top_allocators = memory_profile.get("top_allocators", [])[:5]
        for alloc in top_allocators:
            file_path = alloc.get("file_path", "unknown")
            line_num = alloc.get("line_number", 0)
            alloc_name = alloc.get("name", "unknown")

            key = (file_path, line_num)

            if key in functions_map:
                # Update existing function with memory data
                functions_map[key]["memory_mb"] = alloc.get("memory_mb", 0)
                functions_map[key]["memory_call_count"] = alloc.get("occurrences", 0)
            else:
                # Create new entry if not in CPU profile
                functions_map[key] = {
                    "name": alloc_name,
                    "file_path": file_path,
                    "line_number": line_num,
                    "cpu_percent": None,
                    "cpu_seconds": None,
                    "cpu_call_count": None,
                    "memory_mb": alloc.get("memory_mb", 0),
                    "memory_call_count": alloc.get("occurrences", 0),
                }

        # Extract source code for each function
        functions_list = []
        for func_data in functions_map.values():
            file_path = func_data["file_path"]
            line_num = func_data["line_number"]

            source_code = None
            if self.include_source_code and line_num > 0:
                source_code = self._extract_source_code(file_path, line_num)

            func_entry = {
                "name": func_data["name"],
                "file_path": file_path,
                "line_number": line_num,
                "metrics": {
                    "cpu": {
                        "percent": func_data["cpu_percent"],
                        "seconds": func_data["cpu_seconds"],
                        "call_count": func_data["cpu_call_count"],
                    }
                    if func_data["cpu_percent"] is not None
                    else None,
                    "memory": {
                        "mb": func_data["memory_mb"],
                        "occurrences": func_data["memory_call_count"],
                    }
                    if func_data["memory_mb"] is not None
                    else None,
                },
            }

            if source_code:
                func_entry["source_code"] = source_code

            functions_list.append(func_entry)

        # Build final payload
        return {
            "script_path": script_path,
            "total_duration_seconds": cpu_profile.get("total_duration_seconds", 0),
            "peak_memory_mb": memory_profile.get("peak_memory_mb", 0),
            "baseline_memory_mb": memory_profile.get("baseline_memory_mb", 0),
            "memory_growth_mb": memory_profile.get("memory_growth_mb", 0),
            "functions": functions_list,
        }

    def _parse_response(self, response: Any) -> AnalysisResult:
        """
        Parse Claude's tool call response.

        Args:
            response: Response object from Claude API

        Returns:
            AnalysisResult with parsed data

        Raises:
            ResponseParsingError: If parsing fails
        """
        try:
            # Extract tool use from response
            tool_use = None
            for block in response.content:
                if (
                    hasattr(block, "type")
                    and block.type == "tool_use"
                    and hasattr(block, "name")
                    and block.name == "provide_analysis"
                ):
                    tool_use = block
                    break

            if not tool_use:
                raise ResponseParsingError("No tool_use block found in response")

            data = tool_use.input

            # Extract bottlenecks
            bottlenecks = []
            for b_data in data.get("bottlenecks", [])[:5]:
                suggestions = [
                    Suggestion(
                        description=s.get("description", ""),
                        estimated_improvement=s.get("estimated_improvement", ""),
                        difficulty=s.get("difficulty", "Medium"),
                    )
                    for s in b_data.get("suggestions", [])
                ]

                bottleneck = Bottleneck(
                    rank=b_data.get("rank", 0),
                    function_name=b_data.get("function_name", "unknown"),
                    file_path=b_data.get("file_path", "unknown"),
                    line_number=b_data.get("line_number"),
                    impact_description=b_data.get("impact_description", ""),
                    cpu_percent=b_data.get("cpu_percent"),
                    memory_mb=b_data.get("memory_mb"),
                    suggestions=suggestions,
                )
                bottlenecks.append(bottleneck)

            # Create raw response for debugging
            raw_response = json.dumps(data, indent=2)

            return AnalysisResult(
                summary=data.get("summary", "Analysis complete"),
                bottlenecks=bottlenecks,
                general_recommendations=data.get("general_recommendations", []),
                estimated_total_improvement=data.get("estimated_total_improvement"),
                raw_response=raw_response,
            )

        except (KeyError, ValueError, AttributeError) as e:
            raise ResponseParsingError(f"Invalid response structure: {e}") from e
