# METT Data Portal Client

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/mett-dataportal.svg)](https://badge.fury.io/py/mett-dataportal)

Python client library and command-line interface (CLI) for the METT Data Portal API. Access genomic data, experimental results, and protein interactions for gut microbiome research.

## Features

- 🚀 **High-level Python API** - Clean, intuitive interface for programmatic access
- 💻 **Command-line Interface** - Powerful CLI with tab completion and rich output
- 📊 **Multiple Output Formats** - JSON, TSV, and formatted tables
- 🔒 **Flexible Authentication** - Environment variables or config file support
- 📚 **Comprehensive Documentation** - Auto-generated API reference with examples
- 🔄 **Auto-generated SDK** - Stays in sync with the API schema

## Quick Start

### Installation

```bash
pip install mett-dataportal
```

### CLI Usage

```bash
# List all species
mett species list

# Search genomes
mett genomes search --query "Bacteroides" --per-page 5

# Get gene information
mett genes get BU_ATCC8492_00001
```

### Python API

```python
from mett_dataportal import DataPortalClient

# Initialize client
client = DataPortalClient()

# List species
species = client.list_species()
print(f"Found {len(species)} species")

# Search genomes
result = client.search_genomes(query="Bacteroides", per_page=5)
print(f"Found {len(result.items)} genomes")
```

## Documentation

### Quick Links

- 📖 **[API Reference](docs/reference/api-reference.qmd)** - Complete API documentation with tabbed examples (Quarto format)
- 📘 **[Usage Guide](docs/guides/USAGE.md)** - Detailed usage examples for CLI and Python API
- ⚙️ **[Configuration Guide](docs/guides/CONFIGURATION.md)** - Authentication and configuration options
- 🔧 **[Development Guide](docs/developers/DEVELOPMENT.md)** - Setup, testing, and contributing
- 📦 **[Architecture Guide](docs/developers/ARCHITECTURE.md)** - Package architecture and design decisions

### Viewing API Documentation

The API reference is in Quarto format (`.qmd`). To view it:

```bash
# Generate from OpenAPI spec (if needed)
make docs-generate

# Render to HTML
make docs-render

# Open in browser
open docs/reference/api-reference.html
```

Or use preview mode (auto-reloads on changes):

```bash
make docs-preview
```

The rendered HTML includes interactive tabs showing examples in three formats:
- **Friendly CLI** - High-level `mett` commands
- **Generic CLI** - `mett api request` commands
- **cURL** - Raw HTTP requests

For more information, see the [Documentation README](docs/README.md).

## Installation

### From PyPI

```bash
pip install mett-dataportal
```

### From Source

```bash
git clone https://github.com/your-org/mett-dataportal-client.git
cd mett-dataportal-client
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Requirements

- Python 3.10+
- See `pyproject.toml` for full dependency list

## Project Structure

```
mett-dataportal-client/
├── mett_dataportal/          # Main package
│   ├── cli/                  # CLI commands (organized by API type)
│   │   ├── core/             # Core APIs (system, species, genomes, genes)
│   │   ├── experimental/    # Experimental APIs (drugs, proteomics, etc.)
│   │   └── interactions/    # Interaction APIs (PPI, TTP)
│   ├── client.py             # High-level API client
│   ├── config.py             # Configuration management
│   └── utils.py              # Utility functions
├── mett_dataportal_sdk/      # Auto-generated SDK
├── docs/                      # Documentation
│   ├── guides/                # User guides
│   │   ├── USAGE.md          # Usage examples
│   │   └── CONFIGURATION.md  # Configuration guide
│   ├── developers/            # Developer documentation
│   │   └── DEVELOPMENT.md    # Development guide
│   ├── reference/             # API reference
│   │   ├── api-reference.qmd # Main API reference (Quarto)
│   │   └── cli-examples*.md  # Example files
│   └── assets/                # Static assets (CSS, etc.)
├── scripts/                   # Utility scripts
└── tests/                     # Test suite
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make test && make lint`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/mett-dataportal-client/issues)
- **Documentation**: See [docs/](docs/) directory
- **Email**: data-portal@example.com

## Acknowledgments

Built for the METT Data Portal project. Special thanks to all contributors.

---

**Note**: For development environments without SSL certificates, you may need to set:
```bash
export METT_VERIFY_SSL=false
```
