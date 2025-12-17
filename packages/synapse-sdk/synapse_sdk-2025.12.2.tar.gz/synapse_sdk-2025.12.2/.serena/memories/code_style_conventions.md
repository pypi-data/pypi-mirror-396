# Synapse SDK - Code Style and Conventions

## Formatting Tool

**Ruff** is the primary tool for code formatting and linting.

### Ruff Configuration (from pyproject.toml)

```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "Q"]  # pycodestyle, pyflakes, isort, quotes
ignore = ["W191", "E111", "E114", "E117", "D206", "D300", "Q000", "Q001", "Q002", "Q003", "COM812", "COM819", "ISC001", "ISC002"]

[tool.ruff.lint.pydocstyle]
convention = "google"  # Google-style docstrings

[tool.ruff.format]
quote-style = "single"  # Use single quotes for strings
preview = true
```

## Code Style Guidelines

### Line Length
- Maximum 120 characters per line

### Quotes
- Use **single quotes** for strings (`'example'` not `"example"`)

### Docstrings
- Follow **Google style** docstring convention
- Include docstrings for all public modules, classes, and functions

### Import Organization
- Imports automatically sorted by Ruff (isort rules)
- Standard library first, then third-party, then local imports

### Type Hints
- Use type hints for function parameters and return values (Python 3.10+ style)
- Leverage Pydantic for data validation

### Naming Conventions
- Classes: PascalCase (e.g., `PluginRelease`)
- Functions/methods: snake_case (e.g., `setup_runtime_env`)
- Constants: UPPER_SNAKE_CASE
- Private methods: prefix with underscore (`_private_method`)

## Pre-commit Hooks

The project uses pre-commit hooks (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.10
    hooks:
      - id: ruff
        args: [ --fix ]
      - id: ruff-format
```

Hooks automatically:
1. Run Ruff to fix linting issues
2. Format code with Ruff

## Development Philosophy

### Test-Driven Development (TDD)
- Follow Kent Beck's TDD principles: Red → Green → Refactor
- Write failing test first, implement minimal code to pass, then refactor

### Tidy First Approach
- Separate structural changes from behavioral changes
- Never mix structure and behavior in same commit
- Always make structural changes first

### Commit Discipline
- Only commit when all tests pass
- All linter warnings must be resolved
- Each commit represents single logical unit of work
- Clear commit messages indicating structural vs behavioral changes

## Error Handling
- Proper error handling for all external dependencies
- No exposed sensitive data in logs or error messages
- Graceful handling of resource exhaustion

## Testing Conventions
- Test files: `test_*.py` pattern
- Test classes: `Test*` pattern
- Test functions: `test_*` pattern
- Use pytest markers for categorization
- Write descriptive test names that describe behavior
