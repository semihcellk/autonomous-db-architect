"""
Autonomous DB-Architect — CLI Entry Point
Run: python main.py
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def _cli_callback(event: str, data: dict):
    """Pretty-print pipeline events to the terminal."""
    if event == "stage":
        stage = data.get("stage", "")
        status = data.get("status", "")
        labels = {
            "init":          "🚀  Pipeline",
            "analyst":       "📋  Requirements Analyst",
            "sql_developer": "💾  SQL Developer",
            "reflection":    "🔄  Reflection Loop",
            "d2_designer":   "🎨  D2 Designer",
        }
        label = labels.get(stage, stage)
        if status == "running":
            console.print(f"\n[bold cyan]{label}[/] — [dim]running...[/]")
        elif status == "done":
            console.print(f"[bold green]{label}[/] — [green]✓ done[/]")
        elif "run_id" in data:
            console.print(Panel(
                f"[bold]Run ID:[/] {data['run_id']}",
                title="🏛️  Autonomous DB-Architect",
                border_style="bright_blue",
            ))

    elif event == "reflection":
        icon = "✅" if data["passed"] else "❌"
        color = "green" if data["passed"] else "red"
        console.print(f"  {icon} [bold {color}]Iter {data['iteration']}:[/] {data['message']}")

    elif event == "log":
        agent = data.get("agent", "")
        status = data.get("status", "")
        if status == "generating":
            console.print(f"  [dim]⏳ [{agent}] Generating response...[/]")

    elif event == "error":
        console.print(f"\n[bold red]ERROR:[/] {data['message']}")

    elif event == "result":
        console.print()
        console.print(Panel(
            f"[green]SQL Schema →[/] {data['sql_path']}\n"
            f"[green]D2 Diagram →[/] {data.get('d2_path', 'skipped')}\n"
            f"[green]SVG Output →[/] {data.get('svg_path', 'skipped')}\n"
            f"[dim]Reflection iterations: {data['reflection_iterations']}[/]",
            title="✅  Pipeline Complete",
            border_style="green",
        ))
        if data.get("d2_error"):
            console.print(f"  [yellow]⚠ D2 Warning:[/] {data['d2_error']}")


def main():
    console.print(Panel(
        Markdown("**Autonomous DB-Architect**\nDescribe the database you need in plain English."),
        border_style="bright_blue",
    ))

    try:
        request = console.input("[bold cyan]›[/] ")
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Cancelled.[/]")
        sys.exit(0)

    if not request.strip():
        console.print("[yellow]No input provided. Exiting.[/]")
        sys.exit(0)

    # Import here so core.config validation runs after .env is loaded
    from core.pipeline import run, PipelineError

    try:
        run(request, callback=_cli_callback)
    except PipelineError:
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted.[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()