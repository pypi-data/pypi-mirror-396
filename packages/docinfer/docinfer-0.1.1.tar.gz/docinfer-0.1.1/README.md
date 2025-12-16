# docinfer

A Python package for extracting and inferring metadata from PDF documents using AI-powered analysis.

## Features

- Extract metadata from PDF files
- AI-powered document analysis using LLMs
- CLI tool for easy batch processing
- Flexible configuration and output formatting
- Structured metadata models using Pydantic

## Requirements

- Python 3.12 or higher
- **Ollama** - Required for AI-powered analysis
  - [Install Ollama](https://ollama.ai)
  - Pull a model: `ollama pull gemma3:4b`
- See `pyproject.toml` for full Python dependency list

## Installation

### From GitHub Repository

```bash
pip install git+https://github.com/tidyeval/docinfer.git
```

### From Local Development

Clone the repository and install in editable mode:

```bash
git clone https://github.com/tidyeval/docinfer.git
cd docinfer
pip install -e .
```

## Quick Start

### Using uvx (Recommended)

Run directly without installation using [uvx](https://docs.astral.sh/uv/guides/tools/):

```bash
uvx --from git+https://github.com/tidyeval/docinfer.git docinfer <path-to-pdf>
```

> **Note:** Once published to PyPI, you'll be able to run `uvx docinfer <path-to-pdf>` directly.

### CLI Usage

If you've installed the package locally, run directly:

```bash
docinfer <path-to-pdf>
```

#### Options

- `--model MODEL` - Specify the Ollama model (default: `gemma3:4b`)
  - Example: `docinfer document.pdf --model gemma2`
- `--json` - Output as JSON instead of formatted text
- `--no-ai` - Skip AI analysis and show embedded metadata only
- `--export FILE` - Export results to JSON file
- `--quiet` - Suppress progress output

### Python API

```python
from docinfer.services.pdf_extractor import PDFExtractor
from docinfer.services.ai_analyzer import AIAnalyzer

# Extract PDF content
extractor = PDFExtractor()
content = extractor.extract("document.pdf")

# Analyze with AI
analyzer = AIAnalyzer()
metadata = analyzer.analyze(content)
```

## Project Structure

```
docinfer/
├── src/
│   ├── cli.py              # Command-line interface
│   ├── models/             # Pydantic data models
│   ├── services/           # Core services (PDF extraction, AI analysis)
│   └── prompts/            # AI prompt templates
├── tests/                  # Unit and integration tests
├── specs/                  # Project specifications
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Development

### Setting up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/tidyeval/docinfer.git
   cd docinfer
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

```bash
pytest
```

### Code Quality

The project uses:
- **black** for code formatting
- **ruff** for linting
- **pytest** for testing

## Contributing

Contributions are welcome! Please ensure:
- Code passes linting and formatting checks
- Tests pass with good coverage
- Commit messages are descriptive

## License

See LICENSE file for details.

## Author

Tino Kanngiesser (tinokanngiesser@gmail.com)
