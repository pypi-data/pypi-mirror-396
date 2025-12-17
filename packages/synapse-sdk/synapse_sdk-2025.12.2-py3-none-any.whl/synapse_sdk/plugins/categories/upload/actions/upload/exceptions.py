class ExcelSecurityError(Exception):
    """Exception raised when Excel file security validation fails.

    This exception is raised when an Excel file violates security constraints
    such as file size limits, memory usage limits, or contains potentially
    dangerous content.

    Used during Excel metadata processing to enforce security policies
    and prevent processing of files that could pose security risks.

    Example:
        >>> if file_size > max_size:
        ...     raise ExcelSecurityError(f"File size {file_size} exceeds limit {max_size}")
    """

    pass


class ExcelParsingError(Exception):
    """Exception raised when Excel file parsing encounters errors.

    This exception is raised when an Excel file cannot be parsed due to
    format issues, corruption, or other parsing-related problems that
    prevent successful metadata extraction.

    Used during Excel metadata loading to distinguish parsing errors
    from security violations or other types of errors.

    Example:
        >>> try:
        ...     workbook = load_workbook(excel_file)
        ... except InvalidFileException as e:
        ...     raise ExcelParsingError(f"Failed to parse Excel file: {e}")
    """

    pass
