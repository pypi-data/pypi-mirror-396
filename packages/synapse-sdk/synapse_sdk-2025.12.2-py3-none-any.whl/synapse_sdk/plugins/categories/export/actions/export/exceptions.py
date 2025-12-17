class ExportError(Exception):
    """Base exception for export-related errors.

    This exception is raised when an export operation encounters errors
    that prevent successful completion. It serves as the base class for
    more specific export-related exceptions.

    Used during export processing to handle various error conditions
    such as validation failures, data access errors, or processing issues.

    Example:
        >>> if not validate_export_data(data):
        ...     raise ExportError("Export data validation failed")
    """

    pass


class ExportValidationError(ExportError):
    """Exception raised when export parameter validation fails.

    This exception is raised when export parameters or configuration
    fail validation checks, preventing the export operation from starting.

    Used during parameter validation to distinguish validation errors
    from other types of export failures.

    Example:
        >>> if not storage_exists(storage_id):
        ...     raise ExportValidationError(f"Storage {storage_id} does not exist")
    """

    pass


class ExportTargetError(ExportError):
    """Exception raised when export target handling encounters errors.

    This exception is raised when target-specific operations (assignment,
    ground_truth, task) fail due to data access issues, filter problems,
    or target-specific validation failures.

    Used during target data retrieval and processing to handle target-specific
    errors separately from general export errors.

    Example:
        >>> try:
        ...     results = client.list_assignments(params=filters)
        ... except ClientError as e:
        ...     raise ExportTargetError(f"Failed to retrieve assignments: {e}")
    """

    pass
