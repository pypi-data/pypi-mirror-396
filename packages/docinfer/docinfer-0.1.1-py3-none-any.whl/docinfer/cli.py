"""CLI entry point for PDF Metadata Extractor."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from docinfer.models.config import ExtractionConfig, OutputConfig

console = Console()

# Create the app for direct invocation
app = typer.Typer(
    name="docinfer",
    help="Extract metadata from PDF files using AI.",
    add_completion=False,
)


@app.command()
def main(
    path: Path = typer.Argument(
        ...,
        help="PDF file or directory to process",
        exists=True,
        resolve_path=True,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON instead of formatted text",
    ),
    export: Optional[Path] = typer.Option(
        None,
        "--export",
        help="Export results to JSON file",
    ),
    no_ai: bool = typer.Option(
        False,
        "--no-ai",
        help="Skip AI analysis, show embedded metadata only",
    ),
    model: str = typer.Option(
        "gemma3:4b",
        "--model",
        help="Ollama model to use for AI analysis",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress progress output",
    ),
) -> None:
    """Extract metadata from PDF files.

    Examples:
        docinfer document.pdf
        docinfer ./papers/
        docinfer document.pdf --json
        docinfer document.pdf --no-ai
        docinfer document.pdf --export metadata.json
    """
    # Build configuration
    extraction_config = ExtractionConfig(
        model_name=model,
        skip_ai=no_ai,
    )
    output_config = OutputConfig(
        json_output=json_output,
        export_path=export,
        quiet=quiet,
    )

    # Import here to avoid circular imports and allow lazy loading
    from docinfer.services.output import display_error

    if path.is_file():
        _process_single_file(path, extraction_config, output_config)
    elif path.is_dir():
        _process_directory(path, extraction_config, output_config)
    else:
        display_error(f"Path is neither a file nor directory: {path}", console)
        raise typer.Exit(1)


def _process_single_file(
    file_path: Path,
    extraction_config: ExtractionConfig,
    output_config: OutputConfig,
) -> None:
    """Process a single PDF file."""
    from docinfer.services.output import (
        display_error,
        display_metadata,
        display_warning,
        output_json,
    )
    from docinfer.services.pdf_extractor import extract_embedded_metadata, extract_text

    # Validate file extension
    if file_path.suffix.lower() != ".pdf":
        display_error(f"File is not a PDF: {file_path}", console)
        raise typer.Exit(1)

    # Extract embedded metadata
    try:
        embedded, page_count, warnings = extract_embedded_metadata(file_path)
    except FileNotFoundError:
        display_error(f"File not found: {file_path}", console)
        raise typer.Exit(1)
    except PermissionError:
        display_error(f"Permission denied: {file_path}", console)
        raise typer.Exit(1)
    except ValueError as e:
        display_error(str(e), console)
        raise typer.Exit(1)

    # Extract text for AI analysis
    text_content = ""
    pages_analyzed = 0
    if not extraction_config.skip_ai:
        try:
            text_content, pages_analyzed = extract_text(
                file_path, extraction_config.max_pages
            )
            if not text_content.strip():
                warnings.append("No extractable text found - AI summary unavailable")
        except Exception as e:
            warnings.append(f"Text extraction failed: {e}")

    # Build result
    from docinfer.models.metadata import MetadataResult

    result = MetadataResult(
        file_path=file_path,
        file_name=file_path.name,
        page_count=page_count,
        pages_analyzed=pages_analyzed,
        embedded=embedded,
        ai_generated=None,
        warnings=warnings,
    )

    # AI analysis if enabled and text available
    if not extraction_config.skip_ai and text_content.strip():
        from docinfer.services.ai_analyzer import (
            analyze_content,
            is_ollama_available,
            merge_ai_into_embedded,
        )

        if is_ollama_available(extraction_config.model_name):
            if not output_config.quiet:
                from docinfer.services.output import create_spinner

                with create_spinner("Analyzing with AI..."):
                    ai_metadata = analyze_content(text_content, extraction_config)
            else:
                ai_metadata = analyze_content(text_content, extraction_config)

            if ai_metadata:
                result.ai_generated = ai_metadata
                # Merge AI-extracted data into embedded metadata for missing fields
                result.embedded = merge_ai_into_embedded(result.embedded, ai_metadata)
            else:
                result.warnings.append(
                    "AI analysis failed - showing embedded metadata only"
                )
        else:
            result.warnings.append(
                f"Ollama not available or model '{extraction_config.model_name}' not found. "
                f"Run: ollama pull {extraction_config.model_name}"
            )

    # Output result
    if output_config.json_output:
        json_str = output_json(result)
        console.print(json_str)
    else:
        display_metadata(result, console)

    # Export if requested
    if output_config.export_path:
        json_str = output_json(result)
        output_config.export_path.write_text(json_str)
        if not output_config.quiet:
            console.print(f"\n[green]Exported to:[/green] {output_config.export_path}")

    # Show warnings
    if result.warnings and not output_config.json_output:
        for warning in result.warnings:
            display_warning(warning, console)


def _process_directory(
    directory: Path,
    extraction_config: ExtractionConfig,
    output_config: OutputConfig,
) -> None:
    """Process all PDFs in a directory."""
    from docinfer.services.output import (
        display_batch_result,
        display_error,
        output_json,
    )
    from docinfer.services.pdf_extractor import find_pdfs, process_directory

    pdf_files = find_pdfs(directory)

    if not pdf_files:
        display_error(f"No PDF files found in: {directory}", console)
        raise typer.Exit(1)

    result = process_directory(
        directory, pdf_files, extraction_config, output_config, console
    )

    # Output result
    if output_config.json_output:
        json_str = output_json(result)
        console.print(json_str)
    else:
        display_batch_result(result, console)

    # Export if requested
    if output_config.export_path:
        json_str = output_json(result)
        output_config.export_path.write_text(json_str)
        if not output_config.quiet:
            console.print(f"\n[green]Exported to:[/green] {output_config.export_path}")


if __name__ == "__main__":
    app()
    app()
