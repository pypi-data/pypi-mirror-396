# Baicai Dev

A (not) powerful Python package for AI workflow development, built on top of LangChain and LangGraph frameworks.

## Overview

Baicai Dev is a development toolkit designed to streamline the creation and management of AI workflows. It provides a flexible framework for building, testing, and deploying AI-powered applications using LangChain and LangGraph.

## Features

- Workflow development and management
- Integration with LangChain and LangGraph
- Support for multiple LLM providers
- Development and testing utilities
- Code quality and type checking tools

## Requirements

- Python 3.10 or higher (but less than 3.12)
- Poetry for dependency management

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd baicai-dev
```

2. Install dependencies using Poetry:


> MacOs
    > 1. The torchvision package is trying to use the lzma module. The lzma module depends on the _lzma C extension. To fix this, you need to install the XZ development libraries, which provide the required LZMA support, you can install this using Homebrew: `brew install xz`
    > 2. libomp.dylib for lightgbm, solve by `brew install libomp`

```bash
poetry install
```

## Development Setup

1. Create and activate a virtual environment:

```bash
poetry shell
```

2. Install development dependencies:

```bash
poetry install --with dev
```

## Project Structure

```
baicai-dev/
├── baicai_dev/     # Main package directory
├── tests/          # Test files
├── pyproject.toml  # Project configuration
└── README.md       # This file
```

## Development Tools

The project uses several development tools to maintain code quality:

- **pytest**: For testing
- **mypy**: For static type checking
- **ruff**: For linting and code formatting

## Code Style

The project follows strict code style guidelines:

- Line length: 120 characters
- Indentation: 4 spaces
- Quote style: Double quotes
- Type hints are required

## Testing

Run tests using pytest:

```bash
pytest
```

## License

This project is licensed under the [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.en.html) License.

## Authors

- Zhaoyang tech <gengyabc@aliyun.com>

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Keywords

- Python
- AI
- Workflow
- LangChain
- LangGraph

## Example data

- Fisher, R. (1936). Iris [Dataset]. UCI Machine Learning Repository. <https://doi.org/10.24432/C56C76>.
- This dataset was obtained from the StatLib repository. <https://www.dcc.fc.up.pt/~ltorgo/Regression/cal_housing.html>
- seaborn-data/titanic.csv <https://github.com/mwaskom/seaborn-data/blob/master/titanic.csv>
- Productivity Prediction of Garment Employees [Dataset]. (2020). UCI Machine Learning Repository. <https://doi.org/10.24432/C51S6D>.
