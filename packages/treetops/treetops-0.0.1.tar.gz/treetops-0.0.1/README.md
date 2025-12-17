# Treetops

A simple Python package template for MLOps abstraction.

## Installation

Install the latest stable version from PyPI:

```bash
pip install treetops
```

Or install the development version from source:

```bash
git clone https://github.com/tylerlanigan/treetops.git
cd treetops
# Installs package dependencies, but not dev tools
pip install .
```

## Usage

```python
from treetops.example import hello

# Greet the world
print(hello())
# Output: Hello, World!
```

## Development

### Setup Development Environment

The best practice is to use pyenv to manage your Python versions and venv to isolate your project dependencies.

#### Prerequisites

- pyenv installed (for managing Python versions)
- Git installed

#### Step-by-Step Setup

Clone the repository:

```bash
git clone https://github.com/tylerlanigan/treetops.git
cd treetops
```

Install and activate the required Python version:

```bash
# Install the Python version specified in .python-version (e.g., 3.11.9)
# This step requires pyenv
pyenv install 

# Set the local Python version for this project's directory
pyenv local 
```

Create and activate the standardized virtual environment:

```bash
# Create the virtual environment folder named .venv
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate 
```

Install the package in editable mode with development dependencies:

```bash
# Ensure pip is up-to-date
python -m pip install --upgrade pip

# Install the package in editable mode (-e) along with all [dev] dependencies (pytest, ruff, etc.)
pip install -e ".[dev]"
```

### Working with the Editable Install

Once installed with `pip install -e .[dev]`, any changes you make to the source code will be immediately available without needing to reinstall.

**Run Tests**: Execute the test suite using the development dependency pytest.

```bash
pytest tests/
```

**Run Linter/Formatter**: Use the ruff tool for fast code quality checks and automatic formatting.

```bash
# Check and apply automatic fixes (linting, import sorting)
ruff check --fix . 

# Apply standard formatting (like Black)
ruff format .
```

### Building the Package

The build module prepares the distribution files (.whl and .tar.gz) for PyPI.

```bash
python -m build
# Files are created in the dist/ directory.
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
