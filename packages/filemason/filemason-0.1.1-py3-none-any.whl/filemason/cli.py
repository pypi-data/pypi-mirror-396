"""
CLI interface for FileMason

Provides Typer-based commands for organizing files, inspecting the
generated action plan, and viewing the installed version. This module
primarily serves as the user-facing entry point for the FileMason tool.
"""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Annotated
from filemason.orchestrator import Orchestrator
from filemason.services.classifier import Classifier
from filemason.services.executor import Executor
from filemason.services.planner import Planner
from filemason.services.reader import Reader
from filemason.config.config_loader import load_config
from importlib.metadata import version as get_version, PackageNotFoundError

app = typer.Typer(help="FileMason: Organize files into configured buckets")
console = Console()


def get_orchestrator() -> Orchestrator:
    config = load_config()
    return Orchestrator(
        Reader(),
        Classifier(config["buckets"]),
        Planner(),
        Executor(),
        config,
    )


@app.command()
def organize(
    directory: Annotated[
        Path,
        typer.Argument(help="Directory to organize (defaults to current directory)."),
    ] = Path("."),
    dry: Annotated[
        bool,
        typer.Option(
            "--dry/--no-dry",
            help="Perform a dry-run first. Use --no-dry to execute the plan",
        ),
    ] = True,
):
    """Organize files in the given directory."""
    if not directory.exists():
        console.print(f"[red]Directory does not exist: {directory}[/red]")
        raise typer.Exit(1)

    orchestrator = get_orchestrator()
    result = orchestrator.organize(directory, dry_run=dry)

    output_table = Table(title="Job Report")
    output_table.add_column("Result")
    output_table.add_column("Count")

    output_table.add_row("Dry run", str(result.dry_run))
    output_table.add_row("Files read", str(len(result.read_files)))
    output_table.add_row("Files skipped", str(len(result.skipped_files)))
    output_table.add_row("Files classified", str(len(result.classified_files)))
    output_table.add_row("Files not classified", str(len(result.unclassified_files)))
    output_table.add_row("Actions planned", str(len(result.action_plan.steps)))
    output_table.add_row("Actions taken", str(len(result.actions_taken)))
    output_table.add_row("Actions failed", str(len(result.failed_actions)))

    console.print(output_table)


@app.command()
def get_plan(directory: Path = typer.Argument(".")):
    """Show the action plan without performing any moves."""

    if not directory.exists():
        console.print("[red]Directory does not exist.[/red]")
        raise typer.Exit(1)

    orchestrator = get_orchestrator()
    result = orchestrator.organize(directory, dry_run=True)
    output_table = Table(title="Action Plan")
    output_table.add_column("Step")
    output_table.add_column("File ID")
    output_table.add_column("Action")
    output_table.add_column("Source")
    output_table.add_column("Destination")

    for i, step in enumerate(result.action_plan.steps, start=1):
        output_table.add_row(
            str(i),
            str(step.file_id),
            str(step.action),
            str(step.source),
            str(step.destination),
        )
    console.print(output_table)


@app.command()
def version():
    """Show FileMason version."""
    try:
        __version__ = get_version("filemason")
    except PackageNotFoundError:
        __version__ = "0.0.0"

    console.print(f"filemason {__version__}")


def main():
    """Entry point used by the console_script wrapper."""
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
