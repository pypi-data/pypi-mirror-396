"""Command implementations."""

from typing import Optional

import requests

from cli.ai import ClaudeAnalyzer
from cli.core import APIKeyNotFoundError, UnsupportedLanguageError
from cli.core.detector import detect_language, select_profiler
from cli.formatter import RichFormatter


def run_command(
    script_path: str,
    script_args: list[str],
    duration: Optional[int],
    no_analysis: bool,
    api_key: Optional[str],
    web_url: Optional[str] = None,
    language: Optional[str] = None,
) -> bool:
    """
    Execute the profiling command.

    Args:
        script_path: Path to the script to profile
        script_args: Arguments to pass to the script
        duration: Profiling duration in seconds
        no_analysis: Whether to skip AI analysis
        api_key: Anthropic API key
        web_url: Optional URL to upload results to web service
        language: Optional language override (python).
                  If not provided, auto-detected from file extension.

    Returns:
        True if successful, False otherwise
    """
    formatter = RichFormatter()

    try:
        # Show header
        formatter.print_header("🔍 AI Profiler")

        # Show profiling start
        duration_to_use = duration
        formatter.print_profiling_start(script_path, duration_to_use)

        # Detect or validate language
        try:
            detected_language = detect_language(script_path, language)
            if language:
                formatter.console.print(
                    f"[cyan]Using language:[/cyan] {detected_language} (from --lang option)"
                )
        except UnsupportedLanguageError as e:
            formatter.print_error("Language detection failed", e)
            return False

        # Select profiler based on detected language
        try:
            profiler = select_profiler(detected_language, duration_to_use)
        except UnsupportedLanguageError as e:
            formatter.print_error("Profiler selection failed", e)
            return False

        # Run profiling
        formatter.console.print("[cyan]Starting profiling...[/cyan]")

        result = profiler.profile(
            script_path=script_path,
            script_args=script_args,
        )

        # Check if profiling succeeded
        if not result.success:
            formatter.print_error(
                "Profiling failed", Exception(result.error_message or "Unknown error")
            )
            return False

        formatter.console.print("[green]✓[/green] Profiling complete!")
        formatter.console.print()

        # Convert CPU profile to formatter-compatible format
        cpu_data = {
            "duration_seconds": result.cpu_profile.total_duration_seconds,
            "total_samples": len(result.cpu_profile.top_functions),
            "top_functions": [
                {
                    "name": func.name,
                    "file_path": func.file_path,
                    "line_number": func.line_number,
                    "cpu_time_percent": func.cpu_percent,
                    "cpu_time_seconds": func.cpu_seconds,
                    "call_count": func.call_count,
                }
                for func in result.cpu_profile.top_functions
            ],
        }

        # Convert memory profile to formatter-compatible format
        memory_data = {
            "peak_memory_mb": result.memory_profile.peak_memory_mb,
            "baseline_memory_mb": result.memory_profile.baseline_memory_mb,
            "memory_growth_mb": result.memory_profile.memory_growth_mb,
            "top_allocators": [
                {
                    "name": alloc.name,
                    "file_path": alloc.file_path,
                    "line_number": alloc.line_number,
                    "memory_increment_mb": alloc.memory_mb,
                    "memory_usage_mb": alloc.memory_mb,
                    "occurrences": alloc.occurrences,
                }
                for alloc in result.memory_profile.top_allocators
            ],
        }

        # Display CPU profile
        formatter.print_cpu_profile(cpu_data)

        # Display memory profile
        formatter.print_memory_profile(memory_data)

        # Run AI analysis if not disabled
        if not no_analysis:
            formatter.console.print()
            formatter.console.print("[cyan]Analyzing with AI...[/cyan]")

            try:
                # Initialize analyzer
                analyzer = ClaudeAnalyzer(api_key=api_key)

                # Convert to analysis-compatible format
                analysis_data = result.to_dict()

                # Run analysis
                analysis = analyzer.analyze(analysis_data)

                # Display analysis
                formatter.print_analysis_result(analysis.model_dump())

            except APIKeyNotFoundError as e:
                # API key not found
                formatter.print_error("AI analysis failed: API key not configured", e)
                formatter.console.print()
                formatter.console.print(
                    "[yellow]💡 Tip:[/yellow] Set ANTHROPIC_API_KEY environment variable "
                    "or use --api-key option"
                )
                return False

            except Exception as e:
                # Other analysis errors
                formatter.print_error("AI analysis failed", e)
                return False

        # Upload to web service if requested
        if web_url:
            try:
                # Prepare data for web upload
                upload_data = result.to_dict()
                if "analysis" in locals():
                    upload_data["analysis"] = analysis.model_dump()

                # Send to web service
                response = requests.post(
                    f"{web_url.rstrip('/')}/api/profiles",
                    json=upload_data,
                    timeout=10,
                )
                response.raise_for_status()

                result_data = response.json()
                profile_url = result_data.get("url", "")
                profile_id = result_data.get("id", "")

                formatter.console.print("[green]✓[/green] Profile uploaded successfully!")
                formatter.console.print()
                full_url = f"{web_url.rstrip('/')}{profile_url}"
                formatter.console.print(
                    f"[blue underline]{full_url}[/blue underline] to view the full profiling result"
                )
                formatter.console.print()

            except requests.exceptions.RequestException as e:
                formatter.print_error("Failed to upload to web service", e)
                formatter.console.print()
                formatter.console.print(
                    f"[yellow]💡 Tip:[/yellow] Make sure the web service is running at {web_url}"
                )
                return False

        # Show success
        formatter.console.print()
        formatter.print_success("Profiling and analysis complete!")
        return True

    except KeyboardInterrupt:
        formatter.console.print()
        formatter.console.print("[yellow]Profiling interrupted by user[/yellow]")
        return False

    except Exception as e:
        formatter.print_error("Unexpected error", e)
        return False
