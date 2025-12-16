"""PDF extraction service using pypdf."""

from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from docinfer.models.metadata import EmbeddedMetadata


def extract_embedded_metadata(
    file_path: Path,
) -> tuple[EmbeddedMetadata, int, list[str]]:
    """Extract embedded metadata from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Tuple of (EmbeddedMetadata, page_count, warnings)

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file can't be read
        ValueError: If file is encrypted or corrupted
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    warnings: list[str] = []

    try:
        reader = PdfReader(file_path)
    except PdfReadError as e:
        raise ValueError(f"Invalid or corrupted PDF: {e}")

    # Check for encryption
    if reader.is_encrypted:
        raise ValueError("PDF is password-protected and cannot be read")

    # Get page count
    page_count = len(reader.pages)

    # Extract metadata
    metadata = reader.metadata or {}

    # Helper function to safely extract metadata field
    def get_metadata_field(key: str) -> str | None:
        """Safely extract metadata field using both attribute and dict access."""
        try:
            # Try attribute access first
            if hasattr(metadata, key):
                value = getattr(metadata, key)
                if value:
                    return str(value).strip() if value else None
            # Try dict-like access with common key variations
            for variant in [f"/{key}", f"/{key.capitalize()}", key]:
                if variant in metadata:
                    value = metadata[variant]
                    if value:
                        return str(value).strip() if value else None
            return None
        except Exception:
            return None

    # Parse creation date
    creation_date = None
    try:
        if hasattr(metadata, "creation_date") and metadata.creation_date:
            creation_date = metadata.creation_date
        elif "/CreationDate" in metadata:
            creation_date = metadata["/CreationDate"]
    except Exception:
        warnings.append("Could not parse creation date")

    # Parse modification date
    modification_date = None
    try:
        if hasattr(metadata, "modification_date") and metadata.modification_date:
            modification_date = metadata.modification_date
        elif "/ModDate" in metadata:
            modification_date = metadata["/ModDate"]
    except Exception:
        warnings.append("Could not parse modification date")

    embedded = EmbeddedMetadata(
        title=get_metadata_field("title"),
        author=get_metadata_field("author"),
        subject=get_metadata_field("subject"),
        creator=get_metadata_field("creator"),
        producer=get_metadata_field("producer"),
        creation_date=creation_date,
        modification_date=modification_date,
    )

    return embedded, page_count, warnings


def extract_text(file_path: Path, max_pages: int = 10) -> tuple[str, int]:
    """Extract text content from the first N pages of a PDF.

    Args:
        file_path: Path to the PDF file
        max_pages: Maximum number of pages to extract (default 10)

    Returns:
        Tuple of (extracted_text, pages_analyzed)
    """
    reader = PdfReader(file_path)

    if reader.is_encrypted:
        return "", 0

    pages_to_read = min(len(reader.pages), max_pages)
    text_parts: list[str] = []

    for i in range(pages_to_read):
        page = reader.pages[i]
        page_text = page.extract_text() or ""
        if page_text.strip():
            text_parts.append(page_text)

    return "\n\n".join(text_parts), pages_to_read


def find_pdfs(directory: Path) -> list[Path]:
    """Find all PDF files in a directory.

    Args:
        directory: Directory path to search

    Returns:
        List of PDF file paths, sorted by name
    """
    pdf_files = list(directory.glob("*.pdf"))
    return sorted(pdf_files, key=lambda p: p.name.lower())


def process_directory(
    directory: Path,
    pdf_files: list[Path],
    extraction_config: "ExtractionConfig",
    output_config: "OutputConfig",
    console: "Console",
) -> "BatchResult":
    """Process all PDFs in a directory.

    Args:
        directory: Directory being processed
        pdf_files: List of PDF files to process
        extraction_config: Extraction configuration
        output_config: Output configuration
        console: Rich console for output

    Returns:
        BatchResult with all processing results
    """
    from docinfer.models.config import ExtractionConfig, OutputConfig
    from docinfer.models.metadata import BatchResult, MetadataResult
    from docinfer.services.ai_analyzer import (
        analyze_content,
        is_ollama_available,
        merge_ai_into_embedded,
    )
    from docinfer.services.output import create_batch_progress

    results: list[MetadataResult] = []
    errors: list[dict] = []

    # Check AI availability once
    ai_available = False
    if not extraction_config.skip_ai:
        ai_available = is_ollama_available(extraction_config.model_name)

    with create_batch_progress(len(pdf_files), output_config.quiet) as progress:
        task = progress.add_task("Processing PDFs...", total=len(pdf_files))

        for pdf_file in pdf_files:
            try:
                # Extract embedded metadata
                embedded, page_count, warnings = extract_embedded_metadata(pdf_file)

                # Extract text
                text_content = ""
                pages_analyzed = 0
                if not extraction_config.skip_ai and ai_available:
                    text_content, pages_analyzed = extract_text(
                        pdf_file, extraction_config.max_pages
                    )
                    if not text_content.strip():
                        warnings.append("No extractable text found")

                # AI analysis
                ai_metadata = None
                if ai_available and text_content.strip():
                    ai_metadata = analyze_content(text_content, extraction_config)

                result = MetadataResult(
                    file_path=pdf_file,
                    file_name=pdf_file.name,
                    page_count=page_count,
                    pages_analyzed=pages_analyzed,
                    embedded=embedded,
                    ai_generated=ai_metadata,
                    warnings=warnings,
                )

                # Merge AI-extracted data into embedded metadata for missing fields
                if ai_metadata:
                    result.embedded = merge_ai_into_embedded(
                        result.embedded, ai_metadata
                    )

                results.append(result)

            except Exception as e:
                errors.append({"file": str(pdf_file), "error": str(e)})

            progress.update(task, advance=1)

    return BatchResult(
        directory=directory,
        total_files=len(pdf_files),
        successful=len(results),
        failed=len(errors),
        results=results,
        errors=errors,
    )
