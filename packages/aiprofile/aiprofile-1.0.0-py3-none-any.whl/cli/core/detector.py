"""Language detection and profiler selection.

This module provides language detection and profiler selection with extensible
architecture for future language support. Currently supports Python via Scalene.

Future language support can be added by:
1. Creating a new profiler in packages/cli/src/cli/profilers/<language>/
2. Creating a script runner in packages/cli/src/cli/runner/<language>_runner.py
3. Updating detect_language() to recognize the file extension
4. Updating select_profiler() to return the appropriate profiler instance
"""

from pathlib import Path
from typing import Optional

from cli.core.errors import UnsupportedLanguageError
from cli.profilers import Profiler, ScaleneProfiler


def detect_language(script_path: str, language: Optional[str] = None) -> str:
    """
    Detect or validate the programming language for a script.

    Currently supports: Python

    Args:
        script_path: Path to the script file
        language: Optional language override. If provided, validates it.
                  If not provided, auto-detects from file extension.

    Returns:
        Normalized language name: "python"

    Raises:
        UnsupportedLanguageError: If language is specified but not supported,
                                 or if auto-detection fails.
    """
    if language:
        # Normalize and validate provided language
        lang_lower = language.lower()
        if lang_lower in ("python", "py", "python3"):
            return "python"
        else:
            script_ext = Path(script_path).suffix.lower()
            raise UnsupportedLanguageError(
                f"Unsupported language '{language}'. "
                f"Currently supported: python. "
                f"File extension '{script_ext}' could not be auto-detected."
            )
    else:
        # Auto-detect from file extension
        script_ext = Path(script_path).suffix.lower()
        if script_ext in (".py", ".pyw"):
            return "python"
        else:
            raise UnsupportedLanguageError(
                f"Could not detect language from file extension '{script_ext}'. "
                f"Please specify language with --lang option. "
                f"Currently supported extensions: .py, .pyw"
            )


def select_profiler(language: str, duration_seconds: Optional[int] = None) -> Profiler:
    """
    Select the appropriate profiler for a given language.

    Currently supports: Python via Scalene

    Args:
        language: Normalized language name ("python")
        duration_seconds: Optional profiling duration

    Returns:
        Profiler instance

    Raises:
        UnsupportedLanguageError: If language is not supported
    """
    if language == "python":
        return ScaleneProfiler(duration_seconds=duration_seconds)
    else:
        raise UnsupportedLanguageError(
            f"Unsupported language '{language}'. Currently supported: python"
        )
