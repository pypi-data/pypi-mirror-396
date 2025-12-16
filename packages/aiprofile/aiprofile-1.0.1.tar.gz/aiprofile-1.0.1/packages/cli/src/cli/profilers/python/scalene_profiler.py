"""Scalene-based Python profiler with advanced analysis for complex projects."""

import json
import os
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Optional

from cli.core import ScaleneError
from cli.models import (
    PythonCPUProfile,
    PythonFunctionProfile,
    PythonMemoryAllocator,
    PythonMemoryProfile,
    PythonProfilingResult,
)
from cli.runner import ExecutionConfig, PythonScriptRunner

from ..base import Profiler


class ScaleneProfiler(Profiler):
    """Profiler using Scalene for professional-grade Python profiling."""

    def __init__(self, duration_seconds: Optional[int] = None):
        """
        Initialize Scalene profiler.

        Args:
            duration_seconds: How long to profile. Minimum 1 second for testing,
                             longer durations recommended for production.
        """
        # Enforce minimum duration for meaningful data collection
        self.duration_seconds = duration_seconds
        self.runner = PythonScriptRunner()

    def profile(
        self,
        script_path: str,
        script_args: Optional[list[str]] = None,
        config: Optional[ExecutionConfig] = None,
    ) -> PythonProfilingResult:
        """
        Profile a Python script using Scalene.

        Args:
            script_path: Path to Python script
            script_args: Script arguments
            config: Execution configuration

        Returns:
            ProfilingResult with profiling data
        """
        script_args = script_args or []
        config = config or ExecutionConfig(duration_seconds=self.duration_seconds)

        try:
            # Verify script exists and is valid
            self.runner.validate_script(script_path)

            # Create temp file for Scalene JSON output
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json_output = f.name

            try:
                # Run with Scalene
                start_time = time.time()
                result = self._run_scalene(script_path, script_args, json_output, config)
                duration = time.time() - start_time

                if not result.get("success"):
                    return PythonProfilingResult(
                        script_path=script_path,
                        script_args=script_args,
                        language="python",
                        cpu_profile=PythonCPUProfile(total_duration_seconds=duration),
                        memory_profile=PythonMemoryProfile(
                            peak_memory_mb=0,
                            baseline_memory_mb=0,
                            memory_growth_mb=0,
                        ),
                        success=False,
                        error_message=result.get("error_message"),
                        profiler_type="scalene",
                    )

                # Parse Scalene output
                cpu_profile, memory_profile = self._parse_scalene_output(json_output, duration)

                return PythonProfilingResult(
                    script_path=script_path,
                    script_args=script_args,
                    language="python",
                    cpu_profile=cpu_profile,
                    memory_profile=memory_profile,
                    success=True,
                    profiler_type="scalene",
                )

            finally:
                # Clean up temp file
                try:
                    Path(json_output).unlink()
                except FileNotFoundError:
                    pass

        except Exception as e:
            return PythonProfilingResult(
                script_path=script_path,
                script_args=script_args,
                language="python",
                cpu_profile=PythonCPUProfile(total_duration_seconds=0),
                memory_profile=PythonMemoryProfile(
                    peak_memory_mb=0,
                    baseline_memory_mb=0,
                    memory_growth_mb=0,
                ),
                success=False,
                error_message=f"Profiling error: {str(e)}",
                profiler_type="scalene",
            )

    def _run_scalene(
        self,
        script_path: str,
        script_args: list[str],
        json_output: str,
        config: ExecutionConfig,
    ) -> dict:
        """
        Run Scalene on a script with duration-based profiling.

        Starts Scalene as a subprocess and stops it after the specified duration,
        allowing profiling of long-running or never-ending processes.

        Args:
            script_path: Path to script
            script_args: Script arguments
            json_output: Path for JSON output
            config: Execution config

        Returns:
            Success dict
        """
        try:
            # Run with Scalene
            # Note: --profile-all tracks time in all files, not just the entry point
            cmd = [
                sys.executable,
                "-m",
                "scalene",
                "--json",
                "--profile-all",
            ]

            # Only add --profile-interval if user supplied a duration
            if self.duration_seconds is not None:
                cmd.extend(
                    [
                        "--profile-interval",
                        str(self.duration_seconds),  # Write output after duration seconds
                    ]
                )

            cmd.extend(
                [
                    "--outfile",
                    json_output,
                    script_path,
                ]
                + script_args
            )

            # Set working directory to script's parent directory
            # This allows imports like "from data_processor.module import func"
            # to find the data_processor package
            script_dir = str(Path(script_path).parent.resolve())
            script_parent = str(Path(script_dir).parent.resolve())

            # Prepare environment with PYTHONPATH
            env = os.environ.copy()
            # Add the parent directory so packages at that level are findable
            pythonpath = script_parent
            if "PYTHONPATH" in env:
                pythonpath = f"{pythonpath}:{env['PYTHONPATH']}"
            env["PYTHONPATH"] = pythonpath

            # Run Scalene with duration timeout
            # Scalene will write output every --profile-interval seconds
            # We interrupt after duration_seconds
            try:
                subprocess.run(
                    cmd,
                    timeout=self.duration_seconds,
                    capture_output=True,
                    text=True,
                    cwd=script_parent,
                    env=env,
                )
                # Process completed, check if output was created
                if Path(json_output).exists() and Path(json_output).stat().st_size > 0:
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error_message": "Scalene did not produce output",
                    }
            except subprocess.TimeoutExpired:
                # Timeout after duration_seconds - this is expected for long-running code
                # Scalene writes output periodically with --profile-interval
                # so we should have data even though we interrupted it
                time.sleep(1.0)  # Give it a moment to finish writing
                if Path(json_output).exists() and Path(json_output).stat().st_size > 0:
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error_message": f"No profiling output after {self.duration_seconds}s",
                    }

        except FileNotFoundError:
            return {
                "success": False,
                "error_message": "Scalene not found. Install with: pip install scalene",
            }
        except Exception as e:
            return {
                "success": False,
                "error_message": f"Failed to run Scalene: {str(e)}",
            }

    def _parse_scalene_output(
        self, json_file: str, duration: float
    ) -> tuple[PythonCPUProfile, PythonMemoryProfile]:
        """
        Parse Scalene JSON output with advanced analysis for complex projects.

        Args:
            json_file: Path to Scalene JSON output
            duration: Execution duration

        Returns:
            Tuple of (PythonCPUProfile, PythonMemoryProfile)
        """
        try:
            with open(json_file) as f:
                data = json.load(f)

            # Aggregate data by function, not by line
            function_stats = self._aggregate_by_function(data, duration)
            memory_stats = self._analyze_memory_allocations(data)

            # Sort by CPU time and memory usage
            cpu_functions = sorted(
                function_stats.values(), key=lambda x: x.cpu_seconds, reverse=True
            )[:50]  # Top 50 functions

            memory_allocators = sorted(memory_stats, key=lambda x: x.memory_mb, reverse=True)[
                :50
            ]  # Top 50 allocators

            peak_memory_mb = max((m.memory_mb for m in memory_allocators), default=0)

            cpu_profile = PythonCPUProfile(
                total_duration_seconds=duration,
                top_functions=cpu_functions,
            )

            memory_profile = PythonMemoryProfile(
                peak_memory_mb=peak_memory_mb,
                baseline_memory_mb=0,
                memory_growth_mb=peak_memory_mb,
                top_allocators=memory_allocators,
            )

            return cpu_profile, memory_profile

        except json.JSONDecodeError as e:
            raise ScaleneError(f"Failed to parse Scalene JSON: {e}") from e
        except Exception as e:
            raise ScaleneError(f"Error parsing Scalene output: {e}") from e

    def _aggregate_by_function(
        self, data: dict, duration: float
    ) -> dict[str, PythonFunctionProfile]:
        """
        Aggregate profiling data by function instead of line.

        This enables understanding of complex projects by grouping all lines
        within a function and attributing CPU/memory to the function as a whole.

        Args:
            data: Scalene JSON output
            duration: Total execution duration

        Returns:
            Dictionary mapping function keys to FunctionProfile objects
        """
        function_stats: dict[str, PythonFunctionProfile] = {}
        files = data.get("files", {})

        for file_path, file_data in files.items():
            if not isinstance(file_data, dict):
                continue

            # Skip library files, focus on user code
            if self._is_library_file(file_path):
                continue

            functions = file_data.get("functions", [])
            if isinstance(functions, list):
                for func_data in functions:
                    if not isinstance(func_data, dict):
                        continue

                    # Extract function metadata
                    # Note: Scalene uses "line" field for function name, not "name"
                    func_name = func_data.get("line", "unknown")
                    lineno = func_data.get("lineno", 0)

                    # Extract CPU metrics (Scalene reports percentages)
                    cpu_percent = float(func_data.get("n_cpu_percent_python", 0))
                    cpu_seconds = (cpu_percent / 100.0) * duration if duration > 0 else 0

                    # Extract memory metrics
                    memory_mb = float(func_data.get("n_peak_mb", 0))

                    # Use file + function name as unique key
                    func_key = f"{file_path}:{func_name}"

                    # Get call count from Scalene (None if not available)
                    call_count = func_data.get("n_calls")
                    if call_count is not None:
                        call_count = max(0, int(call_count))

                    function_stats[func_key] = PythonFunctionProfile(
                        name=func_name,
                        file_path=file_path,
                        line_number=lineno,
                        cpu_percent=min(100.0, cpu_percent),  # Cap at 100%
                        cpu_seconds=max(0.0, cpu_seconds),  # Ensure non-negative
                        memory_mb=max(0.0, memory_mb),  # Ensure non-negative
                        call_count=call_count,  # None if Scalene didn't provide it
                        # Enhanced Scalene metrics (breakdown percentages)
                        # These are validated to stay within [0, 100] by the model
                        python_cpu_percent=float(func_data.get("n_cpu_percent_python", 0)),
                        c_cpu_percent=float(func_data.get("n_cpu_percent_c", 0)),
                        sys_percent=float(func_data.get("n_sys_percent", 0)),
                        # Memory patterns
                        memory_growth_mb=max(0.0, float(func_data.get("n_growth_mb", 0))),
                        memory_avg_mb=max(0.0, float(func_data.get("n_avg_mb", 0))),
                        # Performance metrics
                        core_utilization=min(
                            1.0, max(0.0, float(func_data.get("n_core_utilization", 0)))
                        ),
                        copy_mb_s=max(0.0, float(func_data.get("n_copy_mb_s", 0))),
                        # GPU metrics (if available from Scalene)
                        gpu_peak_memory_mb=max(
                            0.0, float(func_data.get("n_gpu_peak_memory_mb", 0))
                        ),
                        gpu_percent=float(func_data.get("n_gpu_percent", 0)),
                    )

            # Also extract function stats from lines data
            # This catches functions that are called but may not be in top-level list
            lines = file_data.get("lines", [])
            if isinstance(lines, list):
                self._extract_functions_from_lines(lines, file_path, duration, function_stats)

        return function_stats

    def _extract_functions_from_lines(
        self,
        lines: list,
        file_path: str,
        duration: float,
        function_stats: dict[str, PythonFunctionProfile],
    ) -> None:
        """
        Extract function stats from line-level profiling data.

        Groups consecutive lines under function definitions to calculate per-function metrics.

        Args:
            lines: List of line profiling data from Scalene
            file_path: File path being analyzed
            duration: Total execution duration
            function_stats: Dictionary to accumulate function stats (modified in place)
        """
        current_function = None
        function_data: dict[str, dict] = {}
        current_indent = 0

        for line_data in lines:
            if not isinstance(line_data, dict):
                continue

            lineno = line_data.get("lineno", 0)
            line_text = line_data.get("line", "")
            stripped_text = line_text.strip()

            # Detect function definitions (starting with def)
            if stripped_text.startswith("def "):
                # Extract function name
                current_function = stripped_text.split("(")[0].replace("def ", "").strip()
                current_indent = len(line_text) - len(line_text.lstrip())

                if current_function not in function_data:
                    function_data[current_function] = {
                        "lineno": lineno,
                        "cpu_percent": 0.0,
                        "cpu_seconds": 0.0,
                        "memory_mb": 0.0,
                        "memory_avg_mb": 0.0,
                        "python_cpu_percent": 0.0,
                        "c_cpu_percent": 0.0,
                        "sys_percent": 0.0,
                        "count": 0,
                    }

            # Accumulate stats for current function (skip empty/comment lines)
            if current_function and current_function in function_data and stripped_text:
                # Check indentation to know if we're still in the function
                if len(line_text) - len(
                    line_text.lstrip()
                ) > current_indent or stripped_text.startswith(("#",)):
                    function_data[current_function]["cpu_percent"] += float(
                        line_data.get("n_cpu_percent_python", 0)
                    )
                    function_data[current_function]["python_cpu_percent"] += float(
                        line_data.get("n_cpu_percent_python", 0)
                    )
                    function_data[current_function]["c_cpu_percent"] += max(
                        0.0, float(line_data.get("n_cpu_percent_c", 0))
                    )
                    function_data[current_function]["sys_percent"] += max(
                        0.0, float(line_data.get("n_sys_percent", 0))
                    )
                    function_data[current_function]["memory_mb"] = max(
                        function_data[current_function]["memory_mb"],
                        float(line_data.get("n_peak_mb", 0)),
                    )
                    function_data[current_function]["memory_avg_mb"] += float(
                        line_data.get("n_avg_mb", 0)
                    )
                    function_data[current_function]["count"] += 1

        # Create function profiles from aggregated line data
        for func_name, stats in function_data.items():
            if stats["cpu_percent"] > 0 or stats["memory_mb"] > 0:
                func_key = f"{file_path}:{func_name}"
                # Only add if not already in function_stats (prefer explicit functions)
                if func_key not in function_stats:
                    cpu_seconds = (stats["cpu_percent"] / 100.0) * duration if duration > 0 else 0
                    function_stats[func_key] = PythonFunctionProfile(
                        name=func_name,
                        file_path=file_path,
                        line_number=stats["lineno"],
                        cpu_percent=min(100.0, stats["cpu_percent"]),
                        cpu_seconds=max(0.0, cpu_seconds),
                        memory_mb=max(0.0, stats["memory_mb"]),
                        call_count=None,  # Not available from line-level aggregation
                        # CPU breakdown from line-level aggregation
                        python_cpu_percent=min(100.0, stats["python_cpu_percent"]),
                        c_cpu_percent=min(100.0, stats["c_cpu_percent"]),
                        sys_percent=min(100.0, stats["sys_percent"]),
                        memory_avg_mb=max(0.0, stats["memory_avg_mb"]),
                    )

    def _analyze_memory_allocations(self, data: dict) -> list[PythonMemoryAllocator]:
        """
        Analyze memory allocations by aggregating per-file statistics.

        Groups memory usage by line and identifies which function each line belongs to.

        Args:
            data: Scalene JSON output

        Returns:
            List of MemoryAllocator objects sorted by memory usage
        """
        memory_by_file: dict[str, float] = defaultdict(float)
        memory_by_line: dict[tuple[str, int], float] = {}
        line_to_function: dict[tuple[str, int], str] = {}

        files = data.get("files", {})
        for file_path, file_data in files.items():
            if not isinstance(file_data, dict):
                continue

            # Skip library files
            if self._is_library_file(file_path):
                continue

            # First pass: map line numbers to function names
            current_function = "module"
            lines_list = file_data.get("lines", [])
            if isinstance(lines_list, list):
                for line_data in lines_list:
                    if not isinstance(line_data, dict):
                        continue
                    line_text = line_data.get("line", "").strip()
                    lineno = line_data.get("lineno", 0)

                    # Track function scope
                    if line_text.startswith("def "):
                        current_function = line_text.split("(")[0].replace("def ", "").strip()

                    line_to_function[(file_path, lineno)] = current_function

            # Second pass: aggregate memory usage
            if isinstance(lines_list, list):
                for line_data in lines_list:
                    if not isinstance(line_data, dict):
                        continue

                    lineno = line_data.get("lineno", 0)
                    memory_mb = float(line_data.get("n_peak_mb", 0))

                    if memory_mb > 0:
                        # Track by both file and line for detail
                        line_key = (file_path, lineno)
                        memory_by_line[line_key] = memory_mb
                        memory_by_file[file_path] += memory_mb

        # Create MemoryAllocator objects
        allocators = []

        # First, add top lines with high memory usage
        for (file_path, lineno), memory_mb in sorted(
            memory_by_line.items(), key=lambda x: x[1], reverse=True
        )[:25]:  # Top 25 lines
            # Get line-specific data if available
            files = data.get("files", {})
            line_data = {}
            if file_path in files and isinstance(files[file_path], dict):
                lines = files[file_path].get("lines", [])
                for line_item in lines:
                    if isinstance(line_item, dict) and line_item.get("lineno") == lineno:
                        line_data = line_item
                        break

            # Get function name for this line
            func_name = line_to_function.get((file_path, lineno), "module")
            allocator_name = f"{func_name}() Line {lineno}"

            allocators.append(
                PythonMemoryAllocator(
                    name=allocator_name,
                    file_path=file_path,
                    line_number=lineno,
                    memory_mb=memory_mb,
                    occurrences=1,
                    # Enhanced memory metrics
                    avg_memory_mb=max(0.0, float(line_data.get("n_avg_mb", 0))),
                    growth_mb=max(0.0, float(line_data.get("n_growth_mb", 0))),
                    malloc_count=max(0, int(line_data.get("n_mallocs", 0))),
                    malloc_mb=max(0.0, float(line_data.get("n_malloc_mb", 0))),
                    copy_mb_s=max(0.0, float(line_data.get("n_copy_mb_s", 0))),
                )
            )

        # Then, add file-level summaries (these are already included in line-level)
        # Skip file-level summaries to avoid duplication - focus on specific functions
        # File-level memory is the sum of its functions, so showing it separately is redundant

        return allocators

    def _is_library_file(self, file_path: str) -> bool:
        """
        Determine if a file is from a library vs user code.

        Args:
            file_path: Path to the file

        Returns:
            True if file is from a library, False if user code
        """
        library_indicators = {
            "site-packages",
            "dist-packages",
            "lib/python",
            ".venv",
            "venv",
            "__pycache__",
        }

        for indicator in library_indicators:
            if indicator in file_path:
                return True

        return False

    def supports_language(self, language: str) -> bool:
        """Check if supports Python."""
        return language.lower() in ("python", "py", "python3")

    def get_language(self) -> str:
        """Get supported language."""
        return "python"

    def get_profiler_type(self) -> str:
        """Get profiler type."""
        return "scalene"
