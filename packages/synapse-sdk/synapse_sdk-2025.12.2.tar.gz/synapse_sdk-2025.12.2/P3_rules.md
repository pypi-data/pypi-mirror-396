# P3 Code Review Rules - Best Practices (Medium)

**Priority Level:** P3 (Medium)
**Focus:** Best practices and maintainability

## 1. Code Quality Standards

- Follows project coding standards and conventions
- DRY principle - eliminates code duplication
- Single Responsibility Principle adherence
- Clear and meaningful variable/function names
- Functions are small and focused

## 2. Documentation Requirements

- Public APIs have comprehensive docstrings
- Complex logic is well-commented
- README and documentation updated for user-facing changes
- Examples provided for new features
- Changelog entries for significant changes

## 3. Error Handling

- Proper exception handling and logging
- User-friendly error messages
- Graceful degradation where possible
- Appropriate error types and status codes
- **Use enums for log messages**: Always use `context.run.log_message_with_code(LogCode.ENUM_VALUE)` instead of plain string key-value dictionaries with `context.run.log_message()`. This ensures type safety, consistency, and centralized message management

## 4. Maintainability

- Code is readable and well-structured
- Dependencies are minimal and justified
- Configuration is externalized appropriately
- Code follows SOLID principles

## Examples

### Error Message Handling (Rule 3)

**❌ WRONG - Using plain string messages:**
```python
context.run.log_message('No metadata strategy configured')
context.run.log_message(f'Failed to process file: {filename}')
```

**✅ CORRECT - Using enum-based log codes:**
```python
# 1. Define LogCode enum in enums.py
class LogCode(str, Enum):
    NO_METADATA_STRATEGY = 'NO_METADATA_STRATEGY'
    FILE_PROCESSING_FAILED = 'FILE_PROCESSING_FAILED'

# 2. Define message templates in LOG_MESSAGES
LOG_MESSAGES = {
    LogCode.NO_METADATA_STRATEGY: {
        'message': 'No metadata strategy configured',
        'level': Context.INFO,
    },
    LogCode.FILE_PROCESSING_FAILED: {
        'message': 'Failed to process file: {}',
        'level': Context.DANGER,
    },
}

# 3. Use in code
context.run.log_message_with_code(LogCode.NO_METADATA_STRATEGY)
context.run.log_message_with_code(LogCode.FILE_PROCESSING_FAILED, filename)
```

**Benefits:**
- Type safety and IDE autocomplete
- Centralized message management
- Consistent log levels
- Easy internationalization support
- Prevents typos and duplicate messages

## Review Guidelines

**Code Quality Checklist:**
- [ ] Follows coding standards
- [ ] No code duplication
- [ ] Single responsibility per function/class
- [ ] Clear naming conventions
- [ ] Functions are appropriately sized

**Documentation Checklist:**
- [ ] Public APIs documented
- [ ] Complex logic commented
- [ ] Documentation updated
- [ ] Examples provided
- [ ] Changelog updated

**Error Handling Checklist:**
- [ ] Proper exception handling
- [ ] User-friendly error messages
- [ ] Graceful degradation
- [ ] Appropriate error types
- [ ] Enums used for log messages (not plain strings)

**Maintainability Checklist:**
- [ ] Code is readable
- [ ] Dependencies justified
- [ ] Configuration externalized
- [ ] SOLID principles followed