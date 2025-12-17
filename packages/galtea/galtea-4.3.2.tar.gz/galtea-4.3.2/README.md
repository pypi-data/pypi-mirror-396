# Galtea SDK

<p align="center">
  <img src="https://galtea.ai/img/galtea_mod.png" alt="Galtea" width="500" height="auto"/>
</p>

<p align="center">
  <strong>Comprehensive AI/LLM Testing & Evaluation Framework</strong>
</p>

<p align="center">
	<a href="https://pypi.org/project/galtea/">
		<img src="https://img.shields.io/pypi/v/galtea.svg" alt="PyPI version">
	</a>
	<a href="https://pypi.org/project/galtea/">
		<img src="https://img.shields.io/pypi/pyversions/galtea.svg" alt="Python versions">
	</a>
	<a href="https://www.apache.org/licenses/LICENSE-2.0">
		<img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License">
	</a>
</p>

## Overview

Galtea SDK empowers AI engineers, ML engineers and data scientists to rigorously test and evaluate their AI products. With a focus on reliability and transparency, Galtea offers:

1. **Automated Test Dataset Generation** - Create comprehensive test datasets tailored to your AI product
2. **Sophisticated Product Evaluation** - Evaluate your AI products across multiple dimensions

## Documentation

**All SDK usage and API documentation has moved to our official docs:** [Galtea SDK Documentation](https://docs.galtea.ai/sdk/introduction)

---

## Development

This project uses Poetry for dependency management and packaging.

### Development Setup

```bash
# Print the command to activate the virtual environment
poetry env activate

# Activate the virtual environment by copy-pasting the command
# Example: C:\Users\user\AppData\Local\pypoetry\Cache\virtualenvs\galtea-MmpOHh8e-py3.12\Scripts\activate.ps1

# Install dependencies
poetry install
```

> Exit the virtual environment with `exit` command.

### Running Tests

Tests are located in the `tests/` directory and cover core functionality including file validation, string utilities, and model utilities.

#### Run All Tests

```bash
# Using Poetry (recommended)
poetry run pytest

# Or using Make
make test

# Using virtual environment directly
python -m pytest tests/
```

#### Run Tests with Verbose Output

```bash
poetry run pytest -v
```

#### Run Specific Test File

```bash
poetry run pytest tests/test_file_validation.py
```

#### Run Specific Test Class or Method

```bash
# Run a specific test class
poetry run pytest tests/test_file_validation.py::TestValidateKnowledgeBaseFile

# Run a specific test method
poetry run pytest tests/test_file_validation.py::TestValidateKnowledgeBaseFile::test_valid_txt_file
```

#### Run Tests with Coverage

```bash
poetry run pytest --cov=galtea --cov-report=html
```

This will generate a coverage report in the `htmlcov/` directory.

### Building the Project

To build the project:

```bash
poetry build
```

This will create distribution packages (wheel and source distribution) in the `dist/` directory.

## License

Apache License 2.0

