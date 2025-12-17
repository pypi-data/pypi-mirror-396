# Synapse SDK - Development Guidelines

## Core Development Philosophy

### Test-Driven Development (TDD)

Follow Kent Beck's TDD principles strictly:

1. **Red Phase**: Write a failing test first
2. **Green Phase**: Implement minimal code to make test pass
3. **Refactor Phase**: Improve code structure without changing behavior

#### TDD Guidelines

- Write the simplest failing test that defines a small increment of functionality
- Use meaningful test names that describe behavior (e.g., `test_should_sum_two_positive_numbers`)
- Make test failures clear and informative
- Write just enough code to make the test pass - no more
- Once tests pass, consider if refactoring is needed
- Repeat the cycle for new functionality
- For defects: Write API-level failing test → Write smallest test replicating problem → Fix both

### Tidy First Approach

Separate all changes into two distinct types:

#### 1. Structural Changes
- Rearranging code without changing behavior
- Examples: renaming, extracting methods, moving code
- Validate with tests before and after
- **Always commit separately** from behavioral changes

#### 2. Behavioral Changes
- Adding or modifying actual functionality
- Only after structural changes are complete
- **Never mix** with structural changes

### Commit Discipline

Only commit when:
1. **ALL tests are passing**
2. **ALL compiler/linter warnings resolved**
3. Change represents **single logical unit of work**
4. Commit message clearly states **structural vs behavioral**

Use small, frequent commits rather than large, infrequent ones.

## Code Quality Standards

### Key Principles

1. **Eliminate duplication ruthlessly**
2. **Express intent clearly** through naming and structure
3. **Make dependencies explicit**
4. **Keep methods small** and focused on single responsibility
5. **Minimize state and side effects**
6. **Use simplest solution** that could possibly work

### Refactoring Guidelines

- Refactor **only when tests are passing** (Green phase)
- Use established refactoring patterns with proper names
- Make **one refactoring change at a time**
- **Run tests after each refactoring step**
- Prioritize refactorings that remove duplication or improve clarity

## Code Review Process

### Priority Levels

Reviews follow systematic P1-P4 rules:

#### P1 - Security and Stability (Critical) 🔴
- Hardcoded secrets/credentials
- SQL injection vulnerabilities
- Exposed sensitive data
- Infinite loops/deadlocks
- Memory leaks
- Data corruption risks

**STOP REVIEW** if P1 issues found - must fix immediately.

#### P2 - Core Functionality (High Priority) 🟡
- Architecture and design issues
- Performance problems
- API design and consistency
- Error handling
- Test coverage

#### P3 - Best Practices (Medium Priority) 🟠
- Code maintainability
- Documentation quality
- Code organization
- Naming conventions
- Design patterns

#### P4 - Code Style (Low Priority) 🔵
- Formatting consistency
- Code style preferences
- Minor readability improvements

### Review Commands

```bash
# Review PR with English comments
/review-pr 123

# Review PR with Korean comments
/review-pr 123 ko
```

### Decision Logic

- **P1, P2, or P3 violations** → Request Changes
- **Only P4 violations or no issues** → Approve

## Plugin Development

**IMPORTANT**: When working with plugins:

- **Always refer to** `synapse_sdk/plugins/README.md` for comprehensive documentation
- Don't rely solely on overview in AGENT.md
- Follow modular development patterns
- Use plugin action structure guidelines
- Study real implementation examples
- Follow migration guides for refactoring

## Documentation Requirements

### Multi-Language Support

**All documentation must be maintained in both English and Korean:**

1. **Primary Language**: English
2. **Required Translation**: Every new document needs Korean version
3. **File Structure**:
   - English: `docs/[file].md`
   - Korean: `docs/i18n/ko/docusaurus-plugin-content-docs/current/[file].md`
4. **Content Consistency**: Korean must match English structure
5. **Technical Terms**: Keep technical terms in English within Korean docs
6. **Code Examples**: Remain unchanged in Korean versions
7. **Update Process**: Update English first, then Korean immediately
8. **Review**: Both versions must be reviewed for accuracy

### Documentation Workflow

1. Create/edit English markdown in `docs/`
2. Update sidebar in `docs/sidebars.ts`
3. Test with `make run-docs`
4. Create Korean translation in `docs/i18n/ko/...`
5. Test with `make run-docs-ko`
6. Commit both versions together

## Security Guidelines

### Critical Security Checks

- **No hardcoded secrets** - Use environment variables or config files
- **Input validation** - Validate and sanitize all user input
- **Proper authentication** - Use JWT tokens, never plain passwords
- **Sensitive data** - Don't expose in logs or error messages
- **No injection vulnerabilities** - SQL, command, XSS, etc.

### Data Integrity

- Validate data before persistence
- Proper transaction management
- Consider backup and recovery
- Thread safety in concurrent code
- Graceful handling of resource exhaustion

## Testing Standards

### Test Organization

```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Fast, isolated tests
├── integration/          # External dependencies
└── [component]/          # Component-specific tests
    └── conftest.py       # Component fixtures
```

### Test Markers

Use appropriate markers:
- `@pytest.mark.unit` - Fast, isolated
- `@pytest.mark.integration` - External deps
- `@pytest.mark.slow` - Long-running
- `@pytest.mark.cli` - CLI tests
- `@pytest.mark.plugin` - Plugin tests

### Test Best Practices

1. Write descriptive test names
2. Keep tests isolated and independent
3. Use fixtures for common setup
4. Use parametrized tests for similar cases
5. Mock external dependencies
6. Assert on behavior, not implementation

## API Integration

### Synapse Backend API

- **Base URL**: `https://api.test.synapse.sh/`
- **Authentication**: `SYNAPSE-Access-Token` header
- **Response Format**: Paginated with `count`, `next`, `previous`, `results`
- **Error Handling**: Korean messages common (e.g., "찾을 수 없습니다.")

### Data Enrichment Pattern

1. Fetch primary data (jobs, serve apps)
2. For each plugin_release ID: Fetch release → plugin details
3. For each agent ID: Fetch agent details
4. Cache frequently accessed data

## Environment Considerations

### Darwin/macOS Specifics

This project is developed on Darwin (macOS). Be aware:

- Unix commands available (ls, grep, find, etc.)
- Use `lsof` for port management
- Use `pkill` for process management
- File system is case-insensitive by default

### Configuration Location

User config: `~/.config/synapse/devtools.json`

Contains:
- Backend host and token
- Agent details (id, name, url, token)
- Plugin storage location
