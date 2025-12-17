# Synapse SDK - Task Completion Checklist

## What to Do When a Task is Completed

### 1. Code Quality Checks

#### Formatting
```bash
# Format all Python code
ruff format .

# Verify formatting
ruff format --check .
```

#### Linting
```bash
# Fix linting issues
ruff check --fix .

# Verify no remaining issues
ruff check .

# For specific directory (excluding tests)
.venv/bin/ruff check synapse_sdk/ --exclude="*/tests/*"
```

### 2. Testing

#### Run Relevant Tests
```bash
# Run all tests
make test

# Or run only relevant tests based on changes
make test-unit          # For quick checks
make test-client        # If client code changed
make test-plugin        # If plugin code changed
make test-cli           # If CLI code changed
```

#### Check Coverage
```bash
# Run with coverage report
make test-coverage

# Open HTML report
open htmlcov/index.html
```

### 3. Documentation Updates

#### For User-Facing Changes

If changes affect users (new features, API changes, behavior changes):

1. **Update Documentation Files**
   - Update relevant `.md` files in `docs/`
   - **IMPORTANT**: Maintain both English and Korean versions
   - English: `docs/[file].md`
   - Korean: `docs/i18n/ko/docusaurus-plugin-content-docs/current/[file].md`

2. **Test Documentation**
   ```bash
   make run-docs     # Test English version
   make run-docs-ko  # Test Korean version
   ```

3. **Consider Changelog**
   - For significant changes, add entry to changelog
   - Note CalVer version format

#### For Code-Level Changes

- Update docstrings if function signatures change
- Follow Google-style docstring convention
- Include type hints in function definitions

### 4. Pre-Commit Verification

```bash
# Run pre-commit hooks
pre-commit run --all-files

# Or let pre-commit run automatically on commit
git commit
```

### 5. Git Commit

#### Commit Requirements Checklist

- [ ] All tests pass
- [ ] Code formatted with Ruff
- [ ] No linting errors
- [ ] Documentation updated (if needed)
- [ ] Both English and Korean docs updated (if user-facing)
- [ ] Clear commit message

#### Commit Message Guidelines

```bash
# Structural change example
git commit -m "Refactor: Extract method for plugin validation"

# Behavioral change example  
git commit -m "Add support for GCS storage provider"

# Bug fix example
git commit -m "Fix memory leak in plugin loader"

# Use the standard format from AGENT.md
git commit -m "$(cat <<'EOF'
Brief description of change

Longer explanation if needed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 6. Pull Request Preparation

#### Before Creating PR

- [ ] All commits follow guidelines above
- [ ] Feature branch up to date with main
- [ ] All tests pass on feature branch
- [ ] Documentation complete and tested

#### PR Requirements

- [ ] Clear, descriptive title
- [ ] Detailed description with motivation
- [ ] Reference to related GitHub issues
- [ ] All tests pass locally
- [ ] Code formatted with Ruff
- [ ] Documentation updated for user-facing changes
- [ ] Changelog entry for significant changes

#### PR Review Process

```bash
# Use review-pr command for systematic review
/review-pr PR_NUMBER       # English comments
/review-pr PR_NUMBER ko    # Korean comments
```

Review follows P1-P4 priority rules:
- P1: Security and Stability (Critical) - Must fix
- P2: Core Functionality (High) - Should fix
- P3: Best Practices (Medium) - Consider fixing
- P4: Code Style (Low) - Optional improvements

#### Review Decision Logic

- P1, P2, or P3 violations → Request Changes
- Only P4 violations or no issues → Approve

### 7. CI/CD Verification

After pushing, verify GitHub Actions pass:

- **Lint workflow**: Runs on push and PR
- **Test workflow**: Runs on PR to main and push to main
  - Uses Python 3.12
  - Installs with `uv sync --extra test`
  - Runs `make test-coverage`

### 8. Clean Up

```bash
# Clean test artifacts
make clean

# Remove build artifacts
rm -rf build/ dist/ *.egg-info
```

## Quick Reference

### Minimal Task Completion

For small changes, minimum steps:

```bash
ruff format .
ruff check --fix .
make test
git add .
git commit -m "message"
git push
```

### Complete Task Completion

For significant changes:

```bash
# 1. Format and lint
ruff format .
ruff check --fix .

# 2. Test
make test-coverage

# 3. Update docs (if needed)
# Edit docs/*.md and docs/i18n/ko/**/*.md
make run-docs  # Verify

# 4. Commit
git add .
git commit -m "detailed message"

# 5. Push and create PR
git push origin branch-name
# Create PR on GitHub
# Use /review-pr for review
```
