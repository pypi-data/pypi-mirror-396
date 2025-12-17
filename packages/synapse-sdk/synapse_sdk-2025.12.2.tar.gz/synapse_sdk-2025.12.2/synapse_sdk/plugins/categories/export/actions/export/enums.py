from enum import Enum

from synapse_sdk.shared.enums import Context


class ExportStatus(str, Enum):
    """Export processing status enumeration.

    Defines the possible states for export operations, data files, and export items
    throughout the export process.

    Attributes:
        SUCCESS: Export completed successfully
        FAILED: Export failed with errors
        STAND_BY: Export waiting to be processed
    """

    SUCCESS = 'success'
    FAILED = 'failed'
    STAND_BY = 'stand_by'


class LogCode(str, Enum):
    """Type-safe logging codes for export operations.

    Enumeration of all possible log events during export processing. Each code
    corresponds to a specific event or error state with predefined message
    templates and log levels.

    The codes are organized by category:
    - Validation codes (VALIDATION_FAILED, STORAGE_VALIDATION_FAILED, etc.)
    - Export processing codes (EXPORT_STARTED, EXPORT_COMPLETED, etc.)
    - File processing codes (ORIGINAL_FILE_EXPORTED, DATA_FILE_EXPORTED, etc.)
    - Error handling codes (TARGET_HANDLER_ERROR, EXPORT_FAILED, etc.)

    Each code maps to a configuration in LOG_MESSAGES with message template
    and appropriate log level.
    """

    STORAGE_VALIDATION_FAILED = 'STORAGE_VALIDATION_FAILED'
    FILTER_VALIDATION_FAILED = 'FILTER_VALIDATION_FAILED'
    TARGET_VALIDATION_FAILED = 'TARGET_VALIDATION_FAILED'
    VALIDATION_FAILED = 'VALIDATION_FAILED'
    EXPORT_STARTED = 'EXPORT_STARTED'
    EXPORT_COMPLETED = 'EXPORT_COMPLETED'
    EXPORT_FAILED = 'EXPORT_FAILED'
    NO_RESULTS_FOUND = 'NO_RESULTS_FOUND'
    RESULTS_RETRIEVED = 'RESULTS_RETRIEVED'
    ORIGINAL_FILE_EXPORTED = 'ORIGINAL_FILE_EXPORTED'
    DATA_FILE_EXPORTED = 'DATA_FILE_EXPORTED'
    FILE_EXPORT_FAILED = 'FILE_EXPORT_FAILED'
    TARGET_HANDLER_ERROR = 'TARGET_HANDLER_ERROR'
    NULL_DATA_DETECTED = 'NULL_DATA_DETECTED'


LOG_MESSAGES = {
    LogCode.STORAGE_VALIDATION_FAILED: {
        'message': 'Storage validation failed.',
        'level': Context.DANGER,
    },
    LogCode.FILTER_VALIDATION_FAILED: {
        'message': 'Filter validation failed.',
        'level': Context.DANGER,
    },
    LogCode.TARGET_VALIDATION_FAILED: {
        'message': 'Target validation failed.',
        'level': Context.DANGER,
    },
    LogCode.VALIDATION_FAILED: {
        'message': 'Validation failed.',
        'level': Context.DANGER,
    },
    LogCode.EXPORT_STARTED: {
        'message': 'Export process started.',
        'level': None,
    },
    LogCode.EXPORT_COMPLETED: {
        'message': 'Export process completed.',
        'level': None,
    },
    LogCode.EXPORT_FAILED: {
        'message': 'Export process failed: {}',
        'level': Context.DANGER,
    },
    LogCode.NO_RESULTS_FOUND: {
        'message': 'No results found for export.',
        'level': Context.WARNING,
    },
    LogCode.RESULTS_RETRIEVED: {
        'message': 'Retrieved {} results for export',
        'level': None,
    },
    LogCode.ORIGINAL_FILE_EXPORTED: {
        'message': 'Original file exported successfully.',
        'level': None,
    },
    LogCode.DATA_FILE_EXPORTED: {
        'message': 'Data file exported successfully.',
        'level': None,
    },
    LogCode.FILE_EXPORT_FAILED: {
        'message': 'Failed to export file: {}',
        'level': Context.DANGER,
    },
    LogCode.TARGET_HANDLER_ERROR: {
        'message': 'Target handler error: {}',
        'level': Context.DANGER,
    },
    LogCode.NULL_DATA_DETECTED: {
        'message': 'Data is null for export item',
        'level': Context.WARNING,
    },
}
