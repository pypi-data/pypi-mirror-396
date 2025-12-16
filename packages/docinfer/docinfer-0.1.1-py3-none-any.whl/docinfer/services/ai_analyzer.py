"""AI analysis service using LangChain and Ollama."""

import subprocess
from typing import Optional

from docinfer.models.config import ExtractionConfig
from docinfer.models.metadata import AIMetadata, EmbeddedMetadata
from docinfer.prompts.metadata import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def is_ollama_running() -> bool:
    """Check if Ollama service is running.

    Returns:
        True if Ollama is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def is_model_available(model_name: str) -> bool:
    """Check if a specific Ollama model is available.

    Args:
        model_name: Name of the model to check (e.g., "gemma2")

    Returns:
        True if model is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return False

        # Check if model name appears in output
        # Handle both "gemma2" and "gemma2:latest" formats
        base_model = model_name.split(":")[0]
        return base_model in result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def is_ollama_available(model_name: str) -> bool:
    """Check if Ollama is running and model is available.

    Args:
        model_name: Name of the model to check

    Returns:
        True if both Ollama is running and model is available
    """
    return is_ollama_running() and is_model_available(model_name)


def analyze_content(text: str, config: ExtractionConfig) -> Optional[AIMetadata]:
    """Analyze document content using AI to generate metadata.

    Args:
        text: Extracted text from PDF
        config: Extraction configuration

    Returns:
        AIMetadata if successful, None if analysis fails
    """
    try:
        from langchain_ollama import ChatOllama

        # Initialize LLM with structured output
        llm = ChatOllama(
            model=config.model_name,
            temperature=config.temperature,
        )

        # Use structured output with Pydantic model
        structured_llm = llm.with_structured_output(AIMetadata)

        # Truncate text if too long (keep first ~8000 chars for context)
        max_chars = 8000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Text truncated...]"

        # Build messages
        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT_TEMPLATE.format(text=text)),
        ]

        # Invoke with timeout handling
        result = structured_llm.invoke(messages)

        if isinstance(result, AIMetadata):
            # Ensure keywords are properly formatted with #
            result.keywords = [
                kw if kw.startswith("#") else f"#{kw}" for kw in result.keywords
            ]
            # Ensure keywords are lowercase
            result.keywords = [kw.lower() for kw in result.keywords]

            # Ensure filename ends with .pdf
            if not result.suggested_filename.endswith(".pdf"):
                result.suggested_filename += ".pdf"

            # Clean up filename
            result.suggested_filename = _clean_filename(result.suggested_filename)

            return result

        return None

    except Exception as e:
        # Log error but don't raise - allow graceful fallback
        import sys

        print(f"AI analysis error: {e}", file=sys.stderr)
        return None


def _clean_filename(filename: str) -> str:
    """Clean and normalize a filename.

    Args:
        filename: Proposed filename

    Returns:
        Cleaned filename
    """
    # Remove any path components
    filename = filename.split("/")[-1].split("\\")[-1]

    # Replace spaces and underscores with hyphens
    filename = filename.replace(" ", "-").replace("_", "-")

    # Convert to lowercase
    filename = filename.lower()

    # Remove multiple consecutive hyphens
    while "--" in filename:
        filename = filename.replace("--", "-")

    # Remove invalid characters (keep alphanumeric, hyphen, dot, brackets)
    valid_chars = set("abcdefghijklmnopqrstuvwxyz0123456789-.[]()")
    filename = "".join(c for c in filename if c in valid_chars)

    # Ensure .pdf extension
    if not filename.endswith(".pdf"):
        filename = filename.rstrip(".") + ".pdf"

    return filename


def merge_ai_into_embedded(
    embedded: EmbeddedMetadata, ai_metadata: AIMetadata
) -> EmbeddedMetadata:
    """Merge AI-extracted metadata into embedded metadata for missing fields.

    When PDF metadata lacks title/author/subject but AI extracted them,
    populate the embedded metadata with AI findings.

    Args:
        embedded: Original embedded metadata from PDF
        ai_metadata: AI-generated metadata with extracted information

    Returns:
        Updated EmbeddedMetadata with missing fields filled from AI data
    """
    # Extract author and title from suggested filename
    # Format: topic-title-[author]-[year].pdf
    filename = ai_metadata.suggested_filename.replace(".pdf", "")
    parts = filename.split("-")

    extracted_author = None
    extracted_title = None

    # Try to extract author and year from filename
    # Typical format: topic-title-author-year
    if len(parts) >= 2:
        # Last part is usually the year (4 digits)
        if parts[-1].isdigit() and len(parts[-1]) == 4:
            # Second to last before year is likely author
            if len(parts) >= 3:
                extracted_author = parts[-2]
        else:
            # If no year, last part might be author
            extracted_author = parts[-1]

        # Everything except last 1-2 parts is the title
        if extracted_author and len(parts) > 2:
            title_parts = parts[:-2] if parts[-1].isdigit() else parts[:-1]
            extracted_title = " ".join(title_parts).title()

    # Create updated metadata with AI-extracted info for missing fields
    return EmbeddedMetadata(
        title=embedded.title or extracted_title,
        author=embedded.author or extracted_author,
        subject=embedded.subject or ai_metadata.category,
        creator=embedded.creator,
        producer=embedded.producer,
        creation_date=embedded.creation_date,
        modification_date=embedded.modification_date,
    )
