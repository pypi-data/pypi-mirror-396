"""Rich output formatting service."""

from contextlib import contextmanager
from typing import Generator

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.tree import Tree

from docinfer.models.metadata import BatchResult, MetadataResult


def display_metadata(result: MetadataResult, console: Console) -> None:
    """Display metadata result with Rich formatting.

    Args:
        result: MetadataResult to display
        console: Rich console for output
    """
    tree = Tree(f"[bold blue]{result.file_name}[/bold blue]")

    # Embedded metadata section
    embedded_section = tree.add("[bold cyan]EMBEDDED METADATA[/bold cyan]")
    embedded = result.embedded

    _add_field(embedded_section, "Title", embedded.title)
    _add_field(embedded_section, "Author", embedded.author)
    _add_field(embedded_section, "Subject", embedded.subject)
    _add_field(embedded_section, "Creator", embedded.creator)
    _add_field(embedded_section, "Producer", embedded.producer)

    if embedded.creation_date:
        embedded_section.add(f"Created: {embedded.creation_date.strftime('%Y-%m-%d')}")
    else:
        embedded_section.add("Created: [dim]Not available[/dim]")

    if embedded.modification_date:
        embedded_section.add(f"Modified: {embedded.modification_date.strftime('%Y-%m-%d')}")
    else:
        embedded_section.add("Modified: [dim]Not available[/dim]")

    embedded_section.add(f"Pages: {result.page_count} (analyzed: {result.pages_analyzed})")

    # AI-generated section
    if result.ai_generated:
        ai_section = tree.add("[bold magenta]AI-GENERATED (via Gemma)[/bold magenta]")
        ai = result.ai_generated

        # Summary with word wrapping
        summary_lines = _wrap_text(ai.summary, 60)
        ai_section.add(f"Summary: {summary_lines[0]}")
        for line in summary_lines[1:]:
            ai_section.add(f"         {line}")

        # Keywords as hashtags
        keywords_str = " ".join(ai.keywords)
        ai_section.add(f"Keywords: {keywords_str}")

        ai_section.add(f"Category: {ai.category}")
        ai_section.add(f"Suggested: [green]{ai.suggested_filename}[/green]")

    panel = Panel(
        tree,
        title="[bold]PDF Metadata[/bold]",
        border_style="blue",
    )
    console.print(panel)


def _add_field(tree: Tree, label: str, value: str | None) -> None:
    """Add a field to the tree with proper formatting for None values."""
    if value:
        tree.add(f"{label}: {value}")
    else:
        tree.add(f"{label}: [dim]Not available[/dim]")


def _wrap_text(text: str, width: int) -> list[str]:
    """Wrap text to specified width."""
    words = text.split()
    lines: list[str] = []
    current_line: list[str] = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines if lines else [""]


def display_error(message: str, console: Console) -> None:
    """Display an error message.

    Args:
        message: Error message to display
        console: Rich console for output
    """
    console.print(f"[bold red]Error:[/bold red] {message}")


def display_warning(message: str, console: Console) -> None:
    """Display a warning message.

    Args:
        message: Warning message to display
        console: Rich console for output
    """
    console.print(f"[yellow]Warning:[/yellow] {message}")


def output_json(result: MetadataResult | BatchResult) -> str:
    """Convert result to JSON string.

    Args:
        result: MetadataResult or BatchResult to serialize

    Returns:
        JSON string representation
    """
    return result.model_dump_json(indent=2)


@contextmanager
def create_spinner(description: str) -> Generator[Progress, None, None]:
    """Create a spinner progress indicator.

    Args:
        description: Text to show with spinner

    Yields:
        Progress context manager
    """
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    )
    with progress:
        progress.add_task(description, total=None)
        yield progress


@contextmanager
def create_batch_progress(total: int, quiet: bool = False) -> Generator[Progress, None, None]:
    """Create a progress bar for batch processing.

    Args:
        total: Total number of items
        quiet: If True, create a no-op progress

    Yields:
        Progress context manager
    """
    if quiet:
        # Create a silent progress that does nothing
        progress = Progress(
            TextColumn(""),
            transient=True,
        )
    else:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            transient=True,
        )

    with progress:
        yield progress


def display_batch_result(result: BatchResult, console: Console) -> None:
    """Display batch processing result.

    Args:
        result: BatchResult to display
        console: Rich console for output
    """
    # Summary panel
    summary = f"""[bold]Batch Processing Complete[/bold]

Directory: {result.directory}
Total files: {result.total_files}
[green]Successful: {result.successful}[/green]
[red]Failed: {result.failed}[/red]
"""

    console.print(Panel(summary, title="Summary", border_style="blue"))

    # Individual results
    if result.results:
        console.print("\n[bold]Results:[/bold]\n")
        for r in result.results:
            title = r.embedded.title or r.file_name
            author = r.embedded.author or "Unknown"
            console.print(f"  [green]✓[/green] {r.file_name}")
            console.print(f"      Title: {title}")
            console.print(f"      Author: {author}")
            if r.ai_generated:
                console.print(f"      Category: {r.ai_generated.category}")
                console.print(f"      Suggested: {r.ai_generated.suggested_filename}")
            console.print()

    # Errors
    if result.errors:
        console.print("\n[bold red]Errors:[/bold red]\n")
        for err in result.errors:
            console.print(f"  [red]✗[/red] {err['file']}")
            console.print(f"      {err['error']}")
