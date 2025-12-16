"""Main CLI application using Typer."""

from pathlib import Path
from typing import Optional

import typer

from cli.commands import run_command

# Version constant
__version__ = "1.0.1"

# Create the main Typer app
app = typer.Typer(
    name="aiprofile",
    help="AI-powered Python profiler with Claude AI insights and optimization recommendations",
    no_args_is_help=True,
)


@app.command(name="run")
def run(
    script: str = typer.Argument(
        ...,
        help="Path to the Python script to profile (.py or .pyw)",
    ),
    script_args: Optional[list[str]] = None,
    duration: Optional[int] = typer.Option(
        None,
        "--duration",
        "-d",
        help="Profiling duration in seconds (default: auto-detect, max 300s)",
        min=1,
        max=300,
    ),
    no_analysis: bool = typer.Option(
        False,
        "--no-analysis",
        help="Skip AI analysis and only show profiling data",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        envvar="ANTHROPIC_API_KEY",
        help="Anthropic API key (defaults to ANTHROPIC_API_KEY env var)",
    ),
    web: Optional[str] = typer.Option(
        None,
        "--web",
        help="URL to aiprofile-web service to upload results (e.g., http://localhost:3000)",
        envvar="AIPROFILE_WEB_URL",
    ),
    lang: Optional[str] = typer.Option(
        None,
        "--lang",
        "-l",
        help=(
            "Programming language (python). "
            "Auto-detected from file extension if not specified. "
            "Future versions will support more languages."
        ),
    ),
) -> None:
    """
    Profile a Python script and get AI-powered insights.

    Supports Python scripts (.py, .pyw).

    Examples:

      # Basic profiling
      aiprofile run my_script.py

      # With script arguments
      aiprofile run my_script.py --input data.csv --output results.json

      # Custom duration
      aiprofile run my_script.py --duration 60

      # Skip AI analysis (no API key needed)
      aiprofile run my_script.py --no-analysis

      # Upload to web service
      aiprofile run my_script.py --web http://localhost:3000

      # Profile complex data processing
      aiprofile run data_processor/main.py --duration 120
    """
    # Validate script exists
    script_path = Path(script)
    if not script_path.exists():
        typer.secho(f"Error: Script not found: {script}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not script_path.is_file():
        typer.secho(f"Error: Not a file: {script}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    # Convert to absolute path
    script_abs = str(script_path.resolve())

    # Run the profiling command
    success = run_command(
        script_path=script_abs,
        script_args=script_args or [],
        duration=duration,
        no_analysis=no_analysis,
        api_key=api_key,
        web_url=web,
        language=lang,
    )

    if not success:
        raise typer.Exit(code=1)


@app.command(name="version")
def version() -> None:
    """Show version information."""
    typer.echo(f"aiprofile version {__version__}")
    typer.echo("AI-powered Python profiler with Claude AI insights")
    typer.echo(f"Homepage: https://github.com/yourusername/aiprofile")
    typer.echo(f"Docs: https://github.com/yourusername/aiprofile#-usage")


if __name__ == "__main__":
    app()
