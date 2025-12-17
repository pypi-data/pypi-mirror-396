# Synapse SDK - Suggested Commands

## Package Management

### Using uv (Modern Python Package Manager)

```bash
# Install uv
pip install uv

# Install dependencies
uv sync

# Install with test dependencies
uv sync --extra test

# Install with all optional dependencies
uv sync --extra all

# Install with devtools
uv sync --extra devtools

# Run Python with uv
uv run python script.py

# Run pytest with uv
uv run python -m pytest
```

## Code Quality

### Formatting and Linting

```bash
# Format all Python files
ruff format .

# Format specific file
ruff format path/to/file.py

# Check formatting without applying
ruff format --check .

# Check and fix linting issues
ruff check --fix .

# Check linting without fixing
ruff check .

# Check specific directory excluding tests
.venv/bin/ruff check synapse_sdk/ --exclude="*/tests/*"
```

### Pre-commit

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## Testing

### Using Make Commands

```bash
# Run all tests
make test

# Run with coverage report
make test-coverage

# Run only unit tests (fast)
make test-unit

# Run only integration tests
make test-integration

# Run CLI tests
make test-cli

# Run storage tests
make test-storage

# Run client tests
make test-client

# Run logger tests
make test-logger

# Run plugin tests
make test-plugin

# Run slow tests
make test-slow

# Run with verbose output
make test-verbose

# Run and stop on first failure
make test-failfast

# Clean test artifacts
make clean
```

### Using pytest Directly

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run specific test file
uv run python -m pytest tests/clients/test_base_client.py

# Run tests with specific marker
uv run python -m pytest tests/ -m "unit"

# Run tests excluding marker
uv run python -m pytest tests/ -m "not slow"

# Run with coverage
uv run python -m pytest tests/ --cov=synapse_sdk --cov-report=html

# Run in parallel
uv run python -m pytest tests/ -n auto

# Run with CI config
uv run python -m pytest -c pytest-ci.ini
```

## Documentation

### Docusaurus Commands

```bash
# Initialize documentation (install dependencies)
make init-docs

# Run development server (English)
make run-docs
# Accessible at http://localhost:3330

# Run development server (Korean)
make run-docs-ko

# Build documentation
make build-docs

# Serve built documentation
make serve-docs
# Accessible at http://localhost:4444

# Build and serve
make build-serve-docs

# Kill documentation server
make kill-docs

# Direct npm commands (from docs/)
cd docs/
npm start                    # Dev server
npm run build               # Build static site
npm run serve               # Serve built site
npm run clear               # Clear cache
npm run typecheck           # Type checking
```

## CLI Usage

```bash
# Main CLI entry point
synapse --help

# Configuration commands
synapse config

# Plugin management
synapse plugin

# Run devtools dashboard
synapse devtools
```

## Package Building and Publishing

```bash
# Build package
uv build

# Publish to PyPI (handled by GitHub Actions)
# See .github/workflows/pypi-publish.yml
```

## Git and Version Control

```bash
# Check status
git status

# Add files
git add .

# Commit (after formatting and tests pass)
git commit -m "message"

# Push to remote
git push origin branch-name
```

## System Utilities (Darwin/macOS)

```bash
# List files
ls -la

# Find files
find . -name "*.py"

# Search in files
grep -r "pattern" .

# Better alternative: use Ruff or ripgrep
rg "pattern"

# Process management
ps aux | grep python
kill -9 PID
pkill -f "process_name"

# Network
lsof -i :PORT              # Check port usage
kill $(lsof -t -i:PORT)    # Kill process on port
```

## Development Workflow

### Before Committing

```bash
# 1. Format code
ruff format .

# 2. Fix linting issues
ruff check --fix .

# 3. Verify no remaining issues
ruff check .

# 4. Run all tests
make test

# 5. Check coverage
make test-coverage

# 6. Commit changes
git add .
git commit -m "message"
```

### Creating Pull Requests

```bash
# 1. Create feature branch
git checkout -b feature-name

# 2. Make changes and commit
# (follow "Before Committing" steps)

# 3. Push to remote
git push origin feature-name

# 4. Use /review-pr command for code review
/review-pr PR_NUMBER
/review-pr PR_NUMBER ko  # For Korean comments
```
