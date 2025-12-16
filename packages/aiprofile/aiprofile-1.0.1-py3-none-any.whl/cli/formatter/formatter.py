"""Rich terminal formatter for profiling results and AI analysis."""

from typing import Any, Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table


class RichFormatter:
    """Formatter for beautiful terminal output using Rich."""

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the formatter.

        Args:
            console: Rich Console instance (creates new one if not provided)
        """
        self.console = console or Console()

    def print_header(self, title: str) -> None:
        """
        Print a header banner.

        Args:
            title: Header title
        """
        self.console.print()
        self.console.rule(f"[bold cyan]{title}[/bold cyan]", style="cyan")
        self.console.print()

    def print_profiling_start(self, script_path: str, duration: int) -> None:
        """
        Print profiling start message.

        Args:
            script_path: Path to script being profiled
            duration: Profile duration in seconds
        """
        self.console.print(
            Panel.fit(
                f"[bold]Profiling:[/bold] [cyan]{script_path}[/cyan]\n"
                f"[bold]Duration:[/bold] {duration} seconds",
                title="🔍 AI Profiler",
                border_style="cyan",
            )
        )
        self.console.print()

    def create_progress(self, description: str = "Profiling...") -> Progress:
        """
        Create a progress indicator.

        Args:
            description: Progress description

        Returns:
            Progress instance
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console,
        )

    def print_cpu_profile(self, cpu_profile: dict[str, Any]) -> None:
        """
        Print CPU profiling results.

        Args:
            cpu_profile: CPU profile data dictionary
        """
        self.console.print("[bold cyan]CPU Profile Results[/bold cyan]")
        self.console.print(
            f"Duration: [yellow]{cpu_profile['duration_seconds']:.2f}s[/yellow] | "
            f"Samples: [yellow]{cpu_profile['total_samples']}[/yellow]"
        )
        self.console.print()

        # Create table for top functions - auto-sized based on terminal width
        table = Table(
            title="Top Functions by CPU Time",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
            padding=(0, 1),
            expand=True,  # Auto-expand to fit terminal width
        )

        table.add_column("Rank", style="cyan", width=4)
        table.add_column("Function", style="green", ratio=2)  # Flexible sizing
        table.add_column("File:Line", style="blue", ratio=2)
        table.add_column("CPU %", justify="right", style="yellow", width=8)
        table.add_column("Time (s)", justify="right", style="yellow", width=10)
        table.add_column("Calls", justify="right", style="white", width=8)

        for i, func in enumerate(cpu_profile.get("top_functions", [])[:10], 1):
            # Color code based on CPU percentage
            cpu_percent = func["cpu_time_percent"]
            if cpu_percent > 20:
                cpu_style = "bold red"
            elif cpu_percent > 10:
                cpu_style = "bold yellow"
            else:
                cpu_style = "yellow"

            # Format call count - show N/A if not available
            call_count = func["call_count"]
            call_count_str = f"{call_count:,}" if call_count is not None else "N/A"

            # Extract just the filename from full path
            import os

            filename = os.path.basename(func["file_path"])

            table.add_row(
                str(i),
                func["name"],
                f"{filename}:{func['line_number']}",
                f"[{cpu_style}]{cpu_percent:.2f}%[/{cpu_style}]",
                f"{func['cpu_time_seconds']:.3f}",
                call_count_str,
            )

        self.console.print(table)
        self.console.print()

    def print_memory_profile(self, memory_profile: dict[str, Any]) -> None:
        """
        Print memory profiling results.

        Args:
            memory_profile: Memory profile data dictionary
        """
        self.console.print("[bold cyan]Memory Profile Results[/bold cyan]")

        peak_mb = memory_profile["peak_memory_mb"]
        baseline_mb = memory_profile["baseline_memory_mb"]
        growth_mb = memory_profile["memory_growth_mb"]

        # Memory summary
        summary_table = Table(
            box=box.SIMPLE,
            show_header=False,
            padding=(0, 2),
        )
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Value", style="yellow")

        summary_table.add_row("Baseline Memory", f"{baseline_mb:.2f} MB")
        summary_table.add_row("Peak Memory", f"{peak_mb:.2f} MB")

        # Color code growth
        if growth_mb > 100:
            growth_style = "bold red"
        elif growth_mb > 50:
            growth_style = "bold yellow"
        else:
            growth_style = "green"

        summary_table.add_row(
            "Memory Growth", f"[{growth_style}]{growth_mb:.2f} MB[/{growth_style}]"
        )

        self.console.print(summary_table)
        self.console.print()

        # Top allocators - wider layout for better readability
        top_allocators = memory_profile.get("top_allocators", [])
        if top_allocators:
            table = Table(
                title="Top Memory Allocators",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold magenta",
                padding=(0, 1),
                expand=True,  # Auto-expand to fit terminal width
            )

            table.add_column("Rank", style="cyan", width=4)
            table.add_column("Allocator", style="green", ratio=2)  # Flexible sizing
            table.add_column("File:Line", style="blue", ratio=2)
            table.add_column("Incr (MB)", justify="right", style="yellow", width=11)
            table.add_column("Total (MB)", justify="right", style="white", width=11)

            for i, alloc in enumerate(top_allocators[:10], 1):
                increment = alloc["memory_increment_mb"]

                # Color code based on increment
                if abs(increment) > 50:
                    increment_style = "bold red"
                elif abs(increment) > 10:
                    increment_style = "bold yellow"
                else:
                    increment_style = "yellow"

                # Extract just the filename from full path
                import os

                filename = os.path.basename(alloc["file_path"])

                table.add_row(
                    str(i),
                    alloc["name"],
                    f"{filename}:{alloc['line_number']}",
                    f"[{increment_style}]{increment:+.2f}[/{increment_style}]",
                    f"{alloc['memory_usage_mb']:.2f}",
                )

            self.console.print(table)
            self.console.print()

    def print_analysis_result(self, analysis: dict[str, Any]) -> None:
        """
        Print AI analysis results.

        Args:
            analysis: Analysis result dictionary
        """
        self.console.print()
        self.console.rule("[bold green]🤖 AI Analysis[/bold green]", style="green")
        self.console.print()

        # Print summary
        summary = analysis.get("summary", "No summary available")
        self.console.print(
            Panel(
                summary,
                title="[bold]Summary[/bold]",
                border_style="green",
                padding=(1, 2),
            )
        )
        self.console.print()

        # Print top bottlenecks
        bottlenecks = analysis.get("bottlenecks", [])
        if bottlenecks:
            self.console.print("[bold yellow]🎯 Top Performance Bottlenecks[/bold yellow]")
            self.console.print()

            for bottleneck in bottlenecks:
                self._print_bottleneck(bottleneck)

        # Print estimated improvement
        total_improvement = analysis.get("estimated_total_improvement")
        if total_improvement:
            self.console.print(
                Panel.fit(
                    f"[bold green]{total_improvement}[/bold green]",
                    title="📈 Estimated Total Improvement",
                    border_style="green",
                )
            )
            self.console.print()

    def _print_bottleneck(self, bottleneck: dict[str, Any]) -> None:
        """
        Print a single bottleneck with its suggestions.

        Args:
            bottleneck: Bottleneck data dictionary
        """
        rank = bottleneck.get("rank", 0)
        function_name = bottleneck.get("function_name", "unknown")
        file_path = bottleneck.get("file_path", "unknown")
        line_number = bottleneck.get("line_number")
        impact = bottleneck.get("impact_description", "")
        cpu_percent = bottleneck.get("cpu_time_percent")
        memory_mb = bottleneck.get("memory_mb")

        # Create header
        location = f"{file_path}:{line_number}" if line_number else file_path

        # Metrics string
        metrics = []
        if cpu_percent is not None:
            metrics.append(f"CPU: {cpu_percent:.1f}%")
        if memory_mb is not None:
            metrics.append(f"Memory: {memory_mb:.1f} MB")
        metrics_str = " | ".join(metrics) if metrics else ""

        # Rank emoji
        rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, "🔸")

        self.console.print(
            f"{rank_emoji} [bold red]Bottleneck #{rank}:[/bold red] [cyan]{function_name}[/cyan]"
        )
        self.console.print(f"   [dim]Location:[/dim] {location}")
        if metrics_str:
            self.console.print(f"   [dim]Metrics:[/dim] {metrics_str}")
        self.console.print(f"   [yellow]{impact}[/yellow]")

        self.console.print()

    def print_error(self, message: str, error: Optional[Exception] = None) -> None:
        """
        Print an error message.

        Args:
            message: Error message
            error: Optional exception object
        """
        error_text = message
        if error:
            error_text += f"\n\n[dim]Details: {str(error)}[/dim]"

        self.console.print(
            Panel(
                error_text,
                title="[bold red]❌ Error[/bold red]",
                border_style="red",
                padding=(1, 2),
            )
        )

    def print_success(self, message: str) -> None:
        """
        Print a success message.

        Args:
            message: Success message
        """
        self.console.print(
            Panel.fit(
                f"[bold green]✓[/bold green] {message}",
                border_style="green",
            )
        )
