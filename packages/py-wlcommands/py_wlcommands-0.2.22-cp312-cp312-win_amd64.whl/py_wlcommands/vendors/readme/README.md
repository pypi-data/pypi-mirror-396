# {project_name}

[![CI](https://github.com/your-username/{project_name}/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/{project_name}/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/{project_name}.svg)](https://badge.fury.io/py/{project_name})
[![Python Versions](https://img.shields.io/pypi/pyversions/{project_name}.svg)](https://pypi.org/project/{project_name}/)

{project_description}

## Features

- **init**: Initialize project environment with Git, virtual environment, i18n, Rust submodule, etc.
- **build**: Execute build tasks, support Python package building and distribution
- **test**: Run project tests
- **format**: Support Python and Rust code formatting (integrated with black, rustfmt, etc.)
- **lint**: Execute code quality checks
- **clean**: Clean build artifacts and temporary files
- **self**: Self-management commands

## Installation

### From PyPI

```bash
pip install {project_name}
```

### From Source

```bash
# Clone the repository
git clone https://github.com/your-username/{project_name}.git
cd {project_name}

# Install in development mode
pip install -e .
```

## Usage

After installation, you can use the `{cli_command}` command:

```bash
# Show help
{cli_command} --help

# Initialize a new project
{cli_command} init

# Build the project
{cli_command} build

# Run tests
{cli_command} test

# Format code
{cli_command} format

# Lint code
{cli_command} lint

# Clean build artifacts
{cli_command} clean

# Update the tool itself
{cli_command} self update
```

## Development

### Prerequisites

- Python >= 3.10
- Rust toolchain (if applicable)
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/{project_name}.git
cd {project_name}

# Install dependencies
pip install -e .

# Or if using uv
uv pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Or using the {cli_command} command
{cli_command} test
```

### Building Distribution Packages

```bash
# Build with {cli_command} command
{cli_command} build dist

# Or directly with maturin (if applicable)
maturin build --release --out dist --sdist
```

## CI/CD

This project uses GitHub Actions for continuous integration and deployment:

- **CI**: Runs tests on multiple platforms (Ubuntu, Windows, macOS) and Python versions (3.10, 3.11, 3.12)
- **Code Quality**: Runs linting and type checking
- **Publish**: Automatically publishes to PyPI when a new tag is pushed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
