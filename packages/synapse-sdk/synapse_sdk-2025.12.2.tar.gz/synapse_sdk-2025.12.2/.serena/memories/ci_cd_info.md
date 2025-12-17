# Synapse SDK - CI/CD Information

## GitHub Actions Workflows

Located in `.github/workflows/`

### 1. Lint Workflow (`lint.yml`)

**Trigger**: On push and pull_request

**Configuration**:
```yaml
name: Lint
on: [push, pull_request]
jobs:
  lint:
    uses: datamaker-kr/workflow/.github/workflows/lint-python.yml@main
```

**Purpose**: 
- Uses shared workflow from datamaker-kr organization
- Runs Python linting checks
- Likely uses Ruff for linting

### 2. Test Workflow (`test.yml`)

**Trigger**: 
- Pull requests to `main` (opened, reopened, synchronize)
- Pushes to `main`

**Configuration**:
```yaml
name: Tests
on:
  pull_request:
    types: [opened, reopened, synchronize]
    branches: [main]
  push:
    branches: [main]
```

**Environment**:
- Runner: `runner-set` (custom runner)
- Python version: 3.12
- Strategy: Matrix testing (fail-fast disabled)

**Steps**:
1. Checkout code (`actions/checkout@v4`)
2. Install uv (`astral-sh/setup-uv@v4` with latest version)
3. Set up Python 3.12 (`uv python install`)
4. Install dependencies (`uv sync --extra test`)
5. Run tests with coverage (`make test-coverage`)

**Coverage Requirements**:
- Uses pytest-cov for coverage reporting
- Generates HTML, XML, and terminal reports
- Coverage thresholds defined in `pytest-ci.ini`

### 3. PyPI Publish Workflow (`pypi-publish.yml`)

**Purpose**: Automated package publishing to PyPI

**Trigger**: Typically on release tags or manual dispatch

## Testing Configuration

### Primary Config (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

addopts = [
    "-v",                    # Verbose
    "--tb=short",            # Short traceback
    "--strict-markers",      # Strict marker validation
    "--disable-warnings",    # Disable warnings
    "--color=yes",           # Colored output
    "--durations=10",        # Show 10 slowest tests
    "--maxfail=5",           # Stop after 5 failures
]

markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (slower, external dependencies)",
    "slow: Slow running tests",
    "cli: Command line interface tests",
    "storage: Storage provider tests",
    "client: Client tests",
    "logger: Logger tests",
    "plugin: Plugin tests",
]

timeout = 300  # 5 minutes per test
```

### CI Config (`pytest-ci.ini`)

Optimized for CI/CD with:
- Parallel test execution (`-n auto`)
- Coverage reporting with thresholds
- JUnit XML output for CI tools
- Optimized for automated environments

## Pre-commit Hooks

**Configuration**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.10
    hooks:
      - id: ruff
        args: [ --fix ]
      - id: ruff-format
```

**Behavior**:
- Runs automatically on `git commit`
- Fixes linting issues with Ruff
- Formats code with Ruff
- Prevents commits if checks fail

**Setup**:
```bash
pre-commit install  # Enable hooks
pre-commit run --all-files  # Run on all files
```

## Build and Release Process

### Package Building

**Tool**: uv (modern Python package manager)

```bash
# Build package
uv build

# Generates:
# - dist/synapse-sdk-{version}.tar.gz (source)
# - dist/synapse_sdk-{version}-py3-none-any.whl (wheel)
```

### Version Management

**Versioning**: CalVer (Calendar Versioning)
- Format: `YYYY.MM.PATCH`
- Managed by setuptools-scm
- Version determined from git tags

```toml
[tool.setuptools_scm]
# Automatic version from git
```

### Publishing

**Automated via GitHub Actions**:
1. Create git tag with CalVer format (e.g., `2025.11.1`)
2. Push tag to GitHub
3. GitHub Action triggers `pypi-publish.yml`
4. Builds and publishes to PyPI

## Local CI Simulation

### Run Tests Like CI

```bash
# Install dependencies like CI
uv sync --extra test

# Run tests with coverage like CI
make test-coverage

# Or use CI config directly
uv run python -m pytest -c pytest-ci.ini
```

### Run Linting Like CI

```bash
# Check formatting
ruff format --check .

# Check linting
ruff check .

# Fix issues
ruff format .
ruff check --fix .
```

## Monitoring and Debugging CI

### Check CI Status

README badges show status:
- ![lint workflow](https://github.com/datamaker-kr/synapse-sdk/actions/workflows/lint.yml/badge.svg)
- ![test workflow](https://github.com/datamaker-kr/synapse-sdk/actions/workflows/test.yml/badge.svg)

### Debugging CI Failures

1. **Check GitHub Actions tab** in repository
2. **Review logs** for failed step
3. **Reproduce locally**:
   ```bash
   uv sync --extra test
   make test-coverage
   ```
4. **Common issues**:
   - Dependency conflicts
   - Missing environment variables
   - Test timeouts
   - Platform-specific issues

### Coverage Reports

**Generated artifacts**:
- `htmlcov/index.html` - HTML report (view locally)
- `coverage.xml` - XML report (for CI tools)
- Terminal output during test run

**Viewing locally**:
```bash
make test-coverage
open htmlcov/index.html  # macOS
```
