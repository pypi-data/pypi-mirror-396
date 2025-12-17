from enum import Enum

from synapse_sdk.shared.enums import Context


class ValidationErrorCode(str, Enum):
    """Validation error codes for Pydantic validators.

    Used in field validators to provide consistent, type-safe error codes
    for resource validation failures.
    """

    MISSING_CONTEXT = 'missing_context'
    STORAGE_NOT_FOUND = 'storage_not_found'
    DATA_COLLECTION_NOT_FOUND = 'data_collection_not_found'
    PROJECT_NOT_FOUND = 'project_not_found'


# Validation error message templates
VALIDATION_ERROR_MESSAGES = {
    ValidationErrorCode.MISSING_CONTEXT: 'Validation context is required.',
    ValidationErrorCode.STORAGE_NOT_FOUND: 'Storage with ID {0} does not exist or is not accessible: {1}',
    ValidationErrorCode.DATA_COLLECTION_NOT_FOUND: 'Data collection with ID {0} does not exist or is not accessible: {1}',
    ValidationErrorCode.PROJECT_NOT_FOUND: 'Project with ID {0} does not exist or is not accessible: {1}',
}


class UploadStatus(str, Enum):
    """Upload processing status enumeration.

    Defines the possible states for upload operations, data files, and data units
    throughout the upload process.

    Attributes:
        SUCCESS: Upload completed successfully
        FAILED: Upload failed with errors
    """

    SUCCESS = 'success'
    FAILED = 'failed'


class LogCode(str, Enum):
    """Type-safe logging codes for upload operations.

    Enumeration of all possible log events during upload processing. Each code
    corresponds to a specific event or error state with predefined message
    templates and log levels.

    The codes are organized by category:
    - Validation codes (VALIDATION_FAILED, STORAGE_VALIDATION_FAILED, etc.)
    - File processing codes (NO_FILES_FOUND, FILES_DISCOVERED, etc.)
    - Excel processing codes (EXCEL_SECURITY_VIOLATION, EXCEL_PARSING_ERROR, etc.)
    - Progress tracking codes (UPLOADING_DATA_FILES, GENERATING_DATA_UNITS, etc.)

    Each code maps to a configuration in LOG_MESSAGES with message template
    and appropriate log level.
    """

    STORAGE_VALIDATION_FAILED = 'STORAGE_VALIDATION_FAILED'
    COLLECTION_VALIDATION_FAILED = 'COLLECTION_VALIDATION_FAILED'
    PROJECT_VALIDATION_FAILED = 'PROJECT_VALIDATION_FAILED'
    VALIDATION_FAILED = 'VALIDATION_FAILED'
    NO_FILES_FOUND = 'NO_FILES_FOUND'
    NO_FILES_UPLOADED = 'NO_FILES_UPLOADED'
    NO_DATA_UNITS_GENERATED = 'NO_DATA_UNITS_GENERATED'
    NO_TYPE_DIRECTORIES = 'NO_TYPE_DIRECTORIES'
    EXCEL_SECURITY_VIOLATION = 'EXCEL_SECURITY_VIOLATION'
    EXCEL_PARSING_ERROR = 'EXCEL_PARSING_ERROR'
    EXCEL_METADATA_LOADED = 'EXCEL_METADATA_LOADED'
    UPLOADING_DATA_FILES = 'UPLOADING_DATA_FILES'
    GENERATING_DATA_UNITS = 'GENERATING_DATA_UNITS'
    IMPORT_COMPLETED = 'IMPORT_COMPLETED'
    TYPE_DIRECTORIES_FOUND = 'TYPE_DIRECTORIES_FOUND'
    TYPE_STRUCTURE_DETECTED = 'TYPE_STRUCTURE_DETECTED'
    FILES_DISCOVERED = 'FILES_DISCOVERED'
    NO_FILES_FOUND_WARNING = 'NO_FILES_FOUND_WARNING'
    FILE_UPLOAD_FAILED = 'FILE_UPLOAD_FAILED'
    DATA_UNIT_BATCH_FAILED = 'DATA_UNIT_BATCH_FAILED'
    FILENAME_TOO_LONG = 'FILENAME_TOO_LONG'
    MISSING_REQUIRED_FILES = 'MISSING_REQUIRED_FILES'
    EXCEL_FILE_NOT_FOUND = 'EXCEL_FILE_NOT_FOUND'
    EXCEL_FILE_VALIDATION_STARTED = 'EXCEL_FILE_VALIDATION_STARTED'
    EXCEL_WORKBOOK_LOADED = 'EXCEL_WORKBOOK_LOADED'
    FILE_ORGANIZATION_STARTED = 'FILE_ORGANIZATION_STARTED'
    BATCH_PROCESSING_STARTED = 'BATCH_PROCESSING_STARTED'
    EXCEL_SECURITY_VALIDATION_STARTED = 'EXCEL_SECURITY_VALIDATION_STARTED'
    EXCEL_MEMORY_ESTIMATION = 'EXCEL_MEMORY_ESTIMATION'
    EXCEL_FILE_NOT_FOUND_PATH = 'EXCEL_FILE_NOT_FOUND_PATH'
    EXCEL_SECURITY_VALIDATION_FAILED = 'EXCEL_SECURITY_VALIDATION_FAILED'
    EXCEL_PARSING_FAILED = 'EXCEL_PARSING_FAILED'
    EXCEL_INVALID_FILE_FORMAT = 'EXCEL_INVALID_FILE_FORMAT'
    EXCEL_FILE_TOO_LARGE = 'EXCEL_FILE_TOO_LARGE'
    EXCEL_FILE_ACCESS_ERROR = 'EXCEL_FILE_ACCESS_ERROR'
    EXCEL_UNEXPECTED_ERROR = 'EXCEL_UNEXPECTED_ERROR'
    # Excel path resolution codes (from HEAD)
    EXCEL_PATH_RESOLVED_STORAGE = 'EXCEL_PATH_RESOLVED_STORAGE'
    EXCEL_PATH_RESOLUTION_FAILED = 'EXCEL_PATH_RESOLUTION_FAILED'
    EXCEL_PATH_RESOLUTION_ERROR = 'EXCEL_PATH_RESOLUTION_ERROR'
    # Asset path codes
    ASSET_PATH_ACCESS_ERROR = 'ASSET_PATH_ACCESS_ERROR'
    ASSET_PATH_NOT_FOUND = 'ASSET_PATH_NOT_FOUND'
    # Step lifecycle codes
    STEP_STARTING = 'STEP_STARTING'
    STEP_COMPLETED = 'STEP_COMPLETED'
    STEP_SKIPPED = 'STEP_SKIPPED'
    STEP_ERROR = 'STEP_ERROR'
    # Rollback codes
    ROLLBACK_INITIALIZATION = 'ROLLBACK_INITIALIZATION'
    ROLLBACK_DATA_UNIT_GENERATION = 'ROLLBACK_DATA_UNIT_GENERATION'
    ROLLBACK_FILE_VALIDATION = 'ROLLBACK_FILE_VALIDATION'
    ROLLBACK_FILE_UPLOADS = 'ROLLBACK_FILE_UPLOADS'
    ROLLBACK_COLLECTION_ANALYSIS = 'ROLLBACK_COLLECTION_ANALYSIS'
    ROLLBACK_FILE_ORGANIZATION = 'ROLLBACK_FILE_ORGANIZATION'
    ROLLBACK_CLEANUP = 'ROLLBACK_CLEANUP'
    # Metadata processing codes
    NO_METADATA_STRATEGY = 'NO_METADATA_STRATEGY'
    METADATA_FILE_ATTRIBUTE_PROCESSING = 'METADATA_FILE_ATTRIBUTE_PROCESSING'
    METADATA_TEMP_FILE_CLEANUP = 'METADATA_TEMP_FILE_CLEANUP'
    METADATA_TEMP_FILE_CLEANUP_FAILED = 'METADATA_TEMP_FILE_CLEANUP_FAILED'
    METADATA_BASE64_DECODED = 'METADATA_BASE64_DECODED'
    METADATA_BASE64_DECODE_FAILED = 'METADATA_BASE64_DECODE_FAILED'
    # Multi-path mode codes
    MULTI_PATH_MODE_ENABLED = 'MULTI_PATH_MODE_ENABLED'
    OPTIONAL_SPEC_SKIPPED = 'OPTIONAL_SPEC_SKIPPED'
    DISCOVERING_FILES_FOR_ASSET = 'DISCOVERING_FILES_FOR_ASSET'
    NO_FILES_FOUND_FOR_ASSET = 'NO_FILES_FOUND_FOR_ASSET'
    FILES_FOUND_FOR_ASSET = 'FILES_FOUND_FOR_ASSET'
    ORGANIZING_FILES_MULTI_PATH = 'ORGANIZING_FILES_MULTI_PATH'
    TYPE_DIRECTORIES_MULTI_PATH = 'TYPE_DIRECTORIES_MULTI_PATH'
    DATA_UNITS_CREATED_FROM_FILES = 'DATA_UNITS_CREATED_FROM_FILES'
    # Cleanup codes
    CLEANUP_WARNING = 'CLEANUP_WARNING'
    CLEANUP_TEMP_DIR_SUCCESS = 'CLEANUP_TEMP_DIR_SUCCESS'
    CLEANUP_TEMP_DIR_FAILED = 'CLEANUP_TEMP_DIR_FAILED'
    # Workflow error codes
    UPLOAD_WORKFLOW_FAILED = 'UPLOAD_WORKFLOW_FAILED'
    UNKNOWN_LOG_CODE = 'UNKNOWN_LOG_CODE'
    # Orchestrator workflow codes
    WORKFLOW_STARTING = 'WORKFLOW_STARTING'
    WORKFLOW_COMPLETED = 'WORKFLOW_COMPLETED'
    WORKFLOW_FAILED = 'WORKFLOW_FAILED'
    STEP_FAILED = 'STEP_FAILED'
    STEP_EXCEPTION = 'STEP_EXCEPTION'
    STEP_TRACEBACK = 'STEP_TRACEBACK'
    ROLLBACK_STARTING = 'ROLLBACK_STARTING'
    ROLLBACK_COMPLETED = 'ROLLBACK_COMPLETED'
    STEP_ROLLBACK = 'STEP_ROLLBACK'
    ROLLBACK_ERROR = 'ROLLBACK_ERROR'
    # Extension filtering codes
    FILES_FILTERED_BY_EXTENSION = 'FILES_FILTERED_BY_EXTENSION'


LOG_MESSAGES = {
    LogCode.STORAGE_VALIDATION_FAILED: {
        'message': 'Storage validation failed.',
        'level': Context.DANGER,
    },
    LogCode.COLLECTION_VALIDATION_FAILED: {
        'message': 'Collection validation failed.',
        'level': Context.DANGER,
    },
    LogCode.PROJECT_VALIDATION_FAILED: {
        'message': 'Project validation failed.',
        'level': Context.DANGER,
    },
    LogCode.VALIDATION_FAILED: {
        'message': 'Validation failed.',
        'level': Context.DANGER,
    },
    LogCode.NO_FILES_FOUND: {
        'message': 'Files not found on the path.',
        'level': Context.WARNING,
    },
    LogCode.NO_FILES_UPLOADED: {
        'message': 'No files were uploaded.',
        'level': Context.WARNING,
    },
    LogCode.NO_DATA_UNITS_GENERATED: {
        'message': 'No data units were generated.',
        'level': Context.WARNING,
    },
    LogCode.NO_TYPE_DIRECTORIES: {
        'message': 'No type-based directory structure found.',
        'level': Context.INFO,
    },
    LogCode.EXCEL_SECURITY_VIOLATION: {
        'message': 'Excel security validation failed: {}',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_PARSING_ERROR: {
        'message': 'Excel parsing failed: {}',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_METADATA_LOADED: {
        'message': 'Excel metadata loaded for {} files',
        'level': None,
    },
    LogCode.UPLOADING_DATA_FILES: {
        'message': 'Uploading data files...',
        'level': None,
    },
    LogCode.GENERATING_DATA_UNITS: {
        'message': 'Generating data units...',
        'level': None,
    },
    LogCode.IMPORT_COMPLETED: {
        'message': 'Import completed.',
        'level': None,
    },
    LogCode.TYPE_DIRECTORIES_FOUND: {
        'message': 'Found type directories: {}',
        'level': None,
    },
    LogCode.TYPE_STRUCTURE_DETECTED: {
        'message': 'Detected type-based directory structure',
        'level': None,
    },
    LogCode.FILES_DISCOVERED: {
        'message': 'Discovered {} files',
        'level': None,
    },
    LogCode.NO_FILES_FOUND_WARNING: {
        'message': 'No files found.',
        'level': Context.WARNING,
    },
    LogCode.FILE_UPLOAD_FAILED: {
        'message': 'Failed to upload file: {}',
        'level': Context.DANGER,
    },
    LogCode.DATA_UNIT_BATCH_FAILED: {
        'message': 'Failed to create data units batch: {}',
        'level': Context.DANGER,
    },
    LogCode.FILENAME_TOO_LONG: {
        'message': 'Skipping file with overly long name: {}...',
        'level': Context.WARNING,
    },
    LogCode.MISSING_REQUIRED_FILES: {
        'message': '{} missing required files: {}',
        'level': Context.WARNING,
    },
    LogCode.EXCEL_FILE_NOT_FOUND: {
        'message': 'Excel metadata file not found: {}',
        'level': Context.WARNING,
    },
    LogCode.EXCEL_FILE_VALIDATION_STARTED: {
        'message': 'Excel file validation started',
        'level': Context.INFO,
    },
    LogCode.EXCEL_WORKBOOK_LOADED: {
        'message': 'Excel workbook loaded successfully',
        'level': Context.INFO,
    },
    LogCode.FILE_ORGANIZATION_STARTED: {
        'message': 'File organization started',
        'level': Context.INFO,
    },
    LogCode.BATCH_PROCESSING_STARTED: {
        'message': 'Batch processing started: {} batches of {} items each',
        'level': Context.INFO,
    },
    LogCode.EXCEL_SECURITY_VALIDATION_STARTED: {
        'message': 'Excel security validation started for file size: {} bytes',
        'level': Context.INFO,
    },
    LogCode.EXCEL_MEMORY_ESTIMATION: {
        'message': 'Excel memory estimation: {} bytes (file) * 3 = {} bytes (estimated)',
        'level': Context.INFO,
    },
    LogCode.EXCEL_FILE_NOT_FOUND_PATH: {
        'message': 'Excel metadata file not found',
        'level': Context.WARNING,
    },
    LogCode.EXCEL_SECURITY_VALIDATION_FAILED: {
        'message': 'Excel security validation failed: {}',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_PARSING_FAILED: {
        'message': 'Excel parsing failed: {}',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_INVALID_FILE_FORMAT: {
        'message': 'Invalid Excel file format: {}',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_FILE_TOO_LARGE: {
        'message': 'Excel file too large to process (memory limit exceeded)',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_FILE_ACCESS_ERROR: {
        'message': 'File access error reading excel metadata: {}',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_UNEXPECTED_ERROR: {
        'message': 'Unexpected error reading excel metadata: {}',
        'level': Context.DANGER,
    },
    # Excel path resolution messages (from HEAD)
    LogCode.EXCEL_PATH_RESOLVED_STORAGE: {
        'message': 'Resolved Excel metadata path relative to storage: {}',
        'level': Context.INFO,
    },
    LogCode.EXCEL_PATH_RESOLUTION_FAILED: {
        'message': 'Storage path resolution failed ({}): {} - trying other strategies',
        'level': Context.INFO,
    },
    LogCode.EXCEL_PATH_RESOLUTION_ERROR: {
        'message': 'Unexpected error resolving storage path ({}): {} - trying other strategies',
        'level': Context.WARNING,
    },
    # Asset path messages
    LogCode.ASSET_PATH_ACCESS_ERROR: {
        'message': 'Error accessing path for {}: {}',
        'level': Context.WARNING,
    },
    LogCode.ASSET_PATH_NOT_FOUND: {
        'message': 'Path does not exist for {}: {}',
        'level': Context.WARNING,
    },
    # Step lifecycle messages
    LogCode.STEP_STARTING: {
        'message': 'Starting step: {}',
        'level': Context.INFO,
    },
    LogCode.STEP_COMPLETED: {
        'message': 'Completed step: {}',
        'level': Context.INFO,
    },
    LogCode.STEP_SKIPPED: {
        'message': 'Skipped step: {}',
        'level': Context.INFO,
    },
    LogCode.STEP_ERROR: {
        'message': 'Error in step {}: {}',
        'level': Context.DANGER,
    },
    # Rollback messages
    LogCode.ROLLBACK_INITIALIZATION: {
        'message': 'Rolling back initialization step',
        'level': Context.INFO,
    },
    LogCode.ROLLBACK_DATA_UNIT_GENERATION: {
        'message': 'Rolled back data unit generation',
        'level': Context.INFO,
    },
    LogCode.ROLLBACK_FILE_VALIDATION: {
        'message': 'Rolled back file validation',
        'level': Context.INFO,
    },
    LogCode.ROLLBACK_FILE_UPLOADS: {
        'message': 'Rolled back file uploads',
        'level': Context.INFO,
    },
    LogCode.ROLLBACK_COLLECTION_ANALYSIS: {
        'message': 'Rolled back collection analysis',
        'level': Context.INFO,
    },
    LogCode.ROLLBACK_FILE_ORGANIZATION: {
        'message': 'Rolled back file organization',
        'level': Context.INFO,
    },
    LogCode.ROLLBACK_CLEANUP: {
        'message': 'Cleanup step rollback - no action needed',
        'level': Context.INFO,
    },
    # Metadata processing messages
    LogCode.NO_METADATA_STRATEGY: {
        'message': 'No metadata strategy configured - skipping metadata processing',
        'level': Context.INFO,
    },
    LogCode.METADATA_FILE_ATTRIBUTE_PROCESSING: {
        'message': 'Processing metadata for file attribute: {}',
        'level': Context.INFO,
    },
    LogCode.METADATA_TEMP_FILE_CLEANUP: {
        'message': 'Cleaned up temporary Excel file: {}',
        'level': Context.INFO,
    },
    LogCode.METADATA_TEMP_FILE_CLEANUP_FAILED: {
        'message': 'Failed to clean up temporary file {}: {}',
        'level': Context.WARNING,
    },
    LogCode.METADATA_BASE64_DECODED: {
        'message': 'Decoded base64 Excel metadata to temporary file: {}',
        'level': Context.INFO,
    },
    LogCode.METADATA_BASE64_DECODE_FAILED: {
        'message': 'Failed to decode base64 Excel metadata: {}',
        'level': Context.DANGER,
    },
    # Multi-path mode messages
    LogCode.MULTI_PATH_MODE_ENABLED: {
        'message': 'Using multi-path mode with {} asset configurations',
        'level': Context.INFO,
    },
    LogCode.OPTIONAL_SPEC_SKIPPED: {
        'message': 'Skipping optional spec {}: no asset path configured',
        'level': Context.INFO,
    },
    LogCode.DISCOVERING_FILES_FOR_ASSET: {
        'message': 'Discovering files for {} (recursive={})',
        'level': Context.INFO,
    },
    LogCode.NO_FILES_FOUND_FOR_ASSET: {
        'message': 'No files found for {}',
        'level': Context.WARNING,
    },
    LogCode.FILES_FOUND_FOR_ASSET: {
        'message': 'Found {} files for {}',
        'level': Context.INFO,
    },
    LogCode.ORGANIZING_FILES_MULTI_PATH: {
        'message': 'Organizing {} files across {} specs',
        'level': Context.INFO,
    },
    LogCode.TYPE_DIRECTORIES_MULTI_PATH: {
        'message': 'Type directories: {}',
        'level': Context.INFO,
    },
    LogCode.DATA_UNITS_CREATED_FROM_FILES: {
        'message': 'Created {} data units from {} files',
        'level': Context.INFO,
    },
    # Cleanup messages
    LogCode.CLEANUP_WARNING: {
        'message': 'Cleanup warning: {}',
        'level': Context.WARNING,
    },
    LogCode.CLEANUP_TEMP_DIR_SUCCESS: {
        'message': 'Cleaned up temporary directory: {}',
        'level': Context.INFO,
    },
    LogCode.CLEANUP_TEMP_DIR_FAILED: {
        'message': 'Failed to cleanup temporary directory: {}',
        'level': Context.WARNING,
    },
    # Workflow error messages
    LogCode.UPLOAD_WORKFLOW_FAILED: {
        'message': 'Upload workflow failed: {}',
        'level': Context.DANGER,
    },
    LogCode.UNKNOWN_LOG_CODE: {
        'message': 'Unknown log code: {}',
        'level': Context.WARNING,
    },
    # Orchestrator workflow messages
    LogCode.WORKFLOW_STARTING: {
        'message': 'Starting upload workflow with {} steps: {}',
        'level': Context.INFO,
    },
    LogCode.WORKFLOW_COMPLETED: {
        'message': 'Upload workflow completed successfully',
        'level': Context.INFO,
    },
    LogCode.WORKFLOW_FAILED: {
        'message': 'Upload workflow failed: {}',
        'level': Context.DANGER,
    },
    LogCode.STEP_FAILED: {
        'message': "Step '{}' failed: {}",
        'level': Context.DANGER,
    },
    LogCode.STEP_EXCEPTION: {
        'message': "Exception in step '{}': {}",
        'level': Context.DANGER,
    },
    LogCode.STEP_TRACEBACK: {
        'message': 'Traceback: {}',
        'level': Context.DANGER,
    },
    LogCode.ROLLBACK_STARTING: {
        'message': 'Starting rollback of {} executed steps',
        'level': Context.WARNING,
    },
    LogCode.ROLLBACK_COMPLETED: {
        'message': 'Rollback completed',
        'level': Context.INFO,
    },
    LogCode.STEP_ROLLBACK: {
        'message': 'Rolling back step: {}',
        'level': Context.INFO,
    },
    LogCode.ROLLBACK_ERROR: {
        'message': "Error rolling back step '{}': {}",
        'level': Context.WARNING,
    },
    # Extension filtering messages
    LogCode.FILES_FILTERED_BY_EXTENSION: {
        'message': 'Filtered {} {} files with unavailable extensions: {} (allowed: {})',
        'level': Context.WARNING,
    },
}
