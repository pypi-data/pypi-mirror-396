# Agentic Resume Builder

A Python library that helps users create professional, impact-oriented resumes through an AI-guided interactive process using Strands Agents SDK and Ollama.

## Features

- **AI-Guided Interview**: Conversational agent that asks targeted questions to extract your professional experiences
- **Impact-Oriented Content**: Automatically formats content with quantifiable metrics and action verbs
- **Markdown-Based**: Uses Markdown as the working format for easy editing and version control
- **PDF Import**: Convert existing PDF resumes to Markdown for editing
- **Professional PDF Output**: Generate polished PDF resumes with customizable styling
- **Local Processing**: All data stays on your machine using Ollama for privacy
- **Session Management**: Save and resume work sessions at your convenience

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [Python API](#python-api)
- [Configuration](#configuration)
- [Examples](#examples)
- [Documentation](#documentation)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Installation

### Prerequisites

- Python 3.9 or higher
- [Ollama](https://ollama.ai/) installed and running locally

### Install Ollama

1. Visit [https://ollama.ai/download](https://ollama.ai/download)
2. Follow installation instructions for your platform
3. Start Ollama: `ollama serve`
4. Pull a model: `ollama pull llama3.2:3b`

### Install from source

```bash
# Clone the repository
git clone <repository-url>
cd agentic-resume-builder

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Install from PyPI (when published)

```bash
pip install agentic-resume-builder
```

## Quick Start

### 1. Create a New Resume

```bash
# Create from default professional template
agentic-resume init my_resume.md

# Or choose a specific template
agentic-resume init my_resume.md --template academic
```

### 2. Start Interactive Session

```bash
# Let the AI guide you through building your resume (uses llama3.2:3b by default)
agentic-resume interactive my_resume.md

# Or use a different Ollama model
agentic-resume --model mistral interactive my_resume.md
agentic-resume --model llama3.2 interactive my_resume.md
```

The AI will ask you questions about your experiences and automatically update your resume with impact-oriented content.

### 3. Generate PDF

```bash
# Create a professional PDF
agentic-resume generate my_resume.md my_resume.pdf
```

### Alternative: Import from Existing PDF

```bash
# Convert your existing PDF resume to Markdown
agentic-resume import old_resume.pdf my_resume.md

# Then continue with interactive session
agentic-resume interactive my_resume.md
```

## CLI Usage

### Global Options

These options can be used with any command:

```bash
--config PATH    # Path to custom configuration file (YAML)
--model MODEL    # Ollama model to use (default: llama3.2:3b)
```

**Examples:**
```bash
# Use a different model for all commands
agentic-resume --model mistral interactive my_resume.md
agentic-resume --model llama3.2 interactive my_resume.md
agentic-resume --model codellama interactive my_resume.md

# Use custom configuration file
agentic-resume --config my_config.yaml interactive my_resume.md

# Combine both options
agentic-resume --config my_config.yaml --model mistral interactive my_resume.md
```

**Popular Ollama Models:**
- `llama3.2:3b` - Default, fast and efficient (3B parameters)
- `llama3.2` - Larger version with better quality (7B+ parameters)
- `mistral` - Alternative high-quality model
- `codellama` - Optimized for technical resumes
- `phi` - Microsoft's efficient model

To install a model: `ollama pull <model_name>`

### Available Commands

#### `init` - Create New Resume

Create a new resume from a template.

```bash
agentic-resume init <output_path> [--template TEMPLATE]

# Examples:
agentic-resume init my_resume.md
agentic-resume init my_resume.md --template academic
agentic-resume init my_resume.md --template technical
```

**Options:**
- `--template`: Template type (professional, academic, technical). Default: professional

#### `load` - Load Existing Resume

Load and validate an existing Markdown resume.

```bash
agentic-resume load <markdown_path>

# Example:
agentic-resume load my_resume.md
```

#### `import` - Import from PDF

Import a resume from PDF format and convert to Markdown.

```bash
agentic-resume import <pdf_path> <output_path>

# Example:
agentic-resume import old_resume.pdf my_resume.md
```

#### `interactive` - Start AI Session

Start an AI-assisted interactive session to build your resume.

```bash
agentic-resume interactive <markdown_path> [--config CONFIG]

# Examples:
agentic-resume interactive my_resume.md
agentic-resume interactive my_resume.md --config custom_config.yaml
```

**Options:**
- `--config`: Path to custom configuration file

**During the session:**
- Answer the AI's questions about your experiences
- The AI will automatically update your resume
- Type `quit` or `exit` to save and exit
- Type `pause` to save and pause the session

#### `generate` - Generate PDF

Generate a professional PDF from your Markdown resume.

```bash
agentic-resume generate <markdown_path> <output_path> [--style STYLE]

# Examples:
agentic-resume generate my_resume.md my_resume.pdf
agentic-resume generate my_resume.md my_resume.pdf --style custom_style.yaml
```

**Options:**
- `--style`: Path to custom PDF style configuration

#### `resume` - Resume Session

Continue a previously saved interactive session.

```bash
agentic-resume resume <session_id>

# Example:
agentic-resume resume 550e8400-e29b-41d4-a716-446655440000
```

**Note:** Session IDs are displayed when you pause or exit an interactive session.

### Getting Help

For detailed help on any command:
```bash
agentic-resume --help
agentic-resume <command> --help
```

## Python API

The library provides a high-level Python API for programmatic use.

### Basic Usage

```python
from agentic_resume_builder import api

# Create a new resume
resume = api.create_resume("my_resume.md", template="professional")

# Load an existing resume
resume = api.load_resume("my_resume.md")

# Import from PDF
resume = api.import_resume_from_pdf("old_resume.pdf", "my_resume.md")

# Generate PDF
api.generate_pdf(resume, "my_resume.pdf")
```

### Interactive Session

```python
from agentic_resume_builder import api

# Load resume
resume = api.load_resume("my_resume.md")

# Start interactive session
session = api.start_interactive_session(resume)

# In a real application, you would present questions to the user
# and process their responses in a loop
```

### Batch Updates

```python
from agentic_resume_builder import api

resume = api.load_resume("my_resume.md")

# Update multiple sections at once
updates = [
    {"section_name": "Summary", "content": "Experienced software engineer..."},
    {"section_name": "Skills", "content": "Python, JavaScript, Go, AWS"}
]
resume = api.batch_update_resume(resume, updates)

# Save changes
api.save_resume(resume)
```

### Complete Workflow

```python
from agentic_resume_builder import api

def my_callback(question):
    """Handle questions from the AI agent."""
    print(question.text)
    return input("Your answer: ")

# Run complete workflow from start to finish
resume = api.complete_workflow(
    input_path="my_resume.md",
    output_pdf_path="my_resume.pdf",
    interactive_callback=my_callback
)
```

### Validation and Statistics

```python
from agentic_resume_builder import api

resume = api.load_resume("my_resume.md")

# Validate resume
validation = api.validate_resume(resume)
if not validation["is_valid"]:
    print("Errors:", validation["errors"])
    print("Warnings:", validation["warnings"])

# Get statistics
stats = api.get_resume_statistics(resume)
print(f"Completeness: {stats['completeness_score']:.1%}")
print(f"Experiences: {stats['num_experiences']}")
print(f"Metrics found: {stats['num_metrics']}")
```

For more examples, see the [examples/](examples/) directory and [API Examples README](examples/API_EXAMPLES_README.md).

## Configuration

You can customize the behavior using a YAML configuration file.

### Configuration File Format

Create a `config.yaml` file:

```yaml
# Ollama Configuration
ollama:
  base_url: "http://localhost:11434"  # Ollama server URL (must be local)
  model: "llama3.2:3b"                      # Model to use
  temperature: 0.7                     # Generation temperature (0.0-2.0)
  timeout: 30                          # Request timeout in seconds

# PDF Style Configuration
pdf_style:
  font_family: "Helvetica"             # Font family
  font_size: 11                        # Base font size
  heading_font_size: 14                # Heading font size
  line_spacing: 1.2                    # Line spacing multiplier
  
  # Margins (in cm)
  margin_top: 2.0
  margin_bottom: 2.0
  margin_left: 2.0
  margin_right: 2.0
  
  # Colors (hex format)
  color_primary: "#000000"             # Primary text color
  color_secondary: "#666666"           # Secondary text color
  color_accent: "#0066cc"              # Accent color for highlights

# Template and Session Directories
templates:
  directory: "./templates"
  default: "professional"

sessions:
  directory: "./sessions"
  auto_save: true
  save_interval: 60                    # Auto-save interval in seconds
```

### Using Configuration

**With CLI:**
```bash
agentic-resume --config config.yaml interactive my_resume.md
```

**With Python API:**
```python
from agentic_resume_builder import ResumeConfig

# Load from YAML
config = ResumeConfig.from_yaml("config.yaml")

# Or create programmatically
from agentic_resume_builder import OllamaConfig, PDFStyle

config = ResumeConfig(
    ollama=OllamaConfig(
        model="llama3.2:3b",
        temperature=0.8
    ),
    pdf_style=PDFStyle(
        font_family="Arial",
        font_size=11
    )
)
```

### Configuration Options

#### Ollama Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `base_url` | string | `http://localhost:11434` | Ollama server URL (must be local) |
| `model` | string | `llama3.2:3b` | Model name to use |
| `temperature` | float | `0.7` | Generation temperature (0.0-2.0) |
| `timeout` | int | `30` | Request timeout in seconds |

**Recommended Models:**
- `llama3.2:3b`: General purpose, good balance
- `llama3`: Improved reasoning
- `mistral`: Fast and efficient
- `codellama`: For technical resumes
- `phi`: Lightweight and fast

#### PDF Style Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `font_family` | string | `Helvetica` | Font family name |
| `font_size` | int | `11` | Base font size in points |
| `heading_font_size` | int | `14` | Heading font size in points |
| `line_spacing` | float | `1.2` | Line spacing multiplier |
| `margin_top` | float | `2.0` | Top margin in cm |
| `margin_bottom` | float | `2.0` | Bottom margin in cm |
| `margin_left` | float | `2.0` | Left margin in cm |
| `margin_right` | float | `2.0` | Right margin in cm |
| `color_primary` | string | `#000000` | Primary text color (hex) |
| `color_secondary` | string | `#666666` | Secondary text color (hex) |
| `color_accent` | string | `#0066cc` | Accent color (hex) |

For more details, see [docs/configuration.md](docs/configuration.md).

## Examples

The `examples/` directory contains comprehensive examples:

- **`api_basic_usage.py`** - Basic API operations (create, load, import, generate)
- **`api_interactive_workflow.py`** - Interactive sessions with the AI agent
- **`api_advanced_patterns.py`** - Advanced patterns and best practices
- **`resume_manager_example.py`** - Using ResumeManager directly
- **`pdf_generator_example.py`** - PDF generation with custom styling
- **`ollama_client_example.py`** - Ollama integration examples

See [examples/API_EXAMPLES_README.md](examples/API_EXAMPLES_README.md) for detailed documentation.

## Documentation

- **[User Guide](docs/user_guide.md)** - Complete guide for end users
- **[API Reference](docs/api_reference.md)** - Detailed API documentation
- **[Configuration Guide](docs/configuration.md)** - Configuration options and examples
- **[Ollama Integration](docs/ollama_integration.md)** - Ollama setup and usage
- **[Agent Tools Usage](docs/agent_tools_usage.md)** - Using agent tools
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[Development Guide](DEVELOPMENT.md)** - For contributors

## Development

### Setup

```bash
# Clone repository
git clone <repository-url>
cd agentic-resume-builder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test types
pytest tests/unit/           # Unit tests only
pytest tests/property/       # Property-based tests only
pytest tests/integration/    # Integration tests only

# Run with coverage
pytest --cov=agentic_resume_builder --cov-report=html

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking (if mypy is installed)
mypy src/
```

### Project Structure

```
agentic-resume-builder/
├── src/agentic_resume_builder/    # Main package
│   ├── __init__.py                # Package initialization & API
│   ├── models.py                  # Data models (Pydantic)
│   ├── exceptions.py              # Custom exceptions
│   ├── config.py                  # Configuration models
│   ├── manager.py                 # Resume manager
│   ├── agent.py                   # AI agent (Strands)
│   ├── agent_tools.py             # Agent tools
│   ├── markdown_processor.py      # Markdown parsing/rendering
│   ├── document_converter.py      # PDF to Markdown conversion
│   ├── pdf_generator.py           # PDF generation
│   ├── session_manager.py         # Session persistence
│   ├── ollama_client.py           # Ollama integration
│   └── cli.py                     # Command-line interface
├── tests/
│   ├── unit/                      # Unit tests
│   ├── property/                  # Property-based tests
│   ├── integration/               # Integration tests
│   └── conftest.py                # Shared fixtures
├── examples/                      # Usage examples
├── docs/                          # Documentation
├── pyproject.toml                 # Project configuration
└── README.md                      # This file
```

For more details, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Troubleshooting

### Ollama Connection Issues

**Problem:** "Could not connect to Ollama"

**Solutions:**
1. Ensure Ollama is running: `ollama serve`
2. Check if Ollama is accessible: `curl http://localhost:11434/api/tags`
3. Verify the port in your configuration matches Ollama's port

### Model Not Found

**Problem:** "Model not found: llama3.2:3b"

**Solutions:**
1. Pull the model: `ollama pull llama3.2:3b`
2. List available models: `ollama list`
3. Use an available model in your configuration

### PDF Generation Fails

**Problem:** "PDF generation failed"

**Solutions:**
1. Check that your Markdown is valid
2. Ensure weasyprint dependencies are installed (see weasyprint docs)
3. Try with default styling first
4. Check file permissions for output directory

### Import from PDF Issues

**Problem:** "PDF conversion produced poor results"

**Solutions:**
1. Ensure the PDF has selectable text (not scanned images)
2. Try manually cleaning up the converted Markdown
3. Consider starting from a template if conversion quality is poor

### Session Not Found

**Problem:** "Session not found"

**Solutions:**
1. Check that the session ID is correct
2. Verify the sessions directory exists and has proper permissions
3. Check if the session file was accidentally deleted

For more troubleshooting help, see [docs/troubleshooting.md](docs/troubleshooting.md).

## Requirements

- Python 3.9 or higher
- Ollama installed and running locally
- Sufficient disk space for models (typically 4-8 GB per model)
- Internet connection for initial model download

## Privacy and Security

- **All processing is local** - No data is sent to external servers
- **No telemetry** - We don't track usage or collect data
- **Session files** are saved with restrictive permissions (600)
- **Your resume data** never leaves your machine

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: See the [docs/](docs/) directory
- **Examples**: Check the [examples/](examples/) directory

## Acknowledgments

- Built with [Strands Agents SDK](https://github.com/strands-ai/strands-agents)
- Powered by [Ollama](https://ollama.ai/)
- PDF conversion using [MarkItDown](https://github.com/microsoft/markitdown)
- PDF generation with [WeasyPrint](https://weasyprint.org/)
