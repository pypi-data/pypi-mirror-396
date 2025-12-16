"""Configuration models for metadata extraction."""

from pathlib import Path

from pydantic import BaseModel, Field


class ExtractionConfig(BaseModel):
    """Configuration for metadata extraction."""

    max_pages: int = Field(
        default=10, description="Maximum pages to analyze", ge=1, le=100
    )
    model_name: str = Field(default="gemma3:4b", description="Ollama model to use")
    skip_ai: bool = Field(default=False, description="Skip AI analysis")
    temperature: float = Field(
        default=0.0, description="LLM temperature", ge=0.0, le=2.0
    )
    timeout_seconds: int = Field(default=120, description="AI analysis timeout", ge=10)


class OutputConfig(BaseModel):
    """Configuration for output formatting."""

    json_output: bool = Field(default=False, description="Output as JSON")
    export_path: Path | None = Field(default=None, description="Export to file")
    quiet: bool = Field(default=False, description="Suppress progress output")
