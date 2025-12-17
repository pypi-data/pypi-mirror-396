from enum import Enum

from synapse_sdk.shared.enums import Context


class AnnotationMethod(str, Enum):
    FILE = 'file'
    INFERENCE = 'inference'


class AnnotateTaskDataStatus(str, Enum):
    SUCCESS = 'success'
    FAILED = 'failed'


class LogCode(str, Enum):
    """Type-safe logging codes for to_task operations.

    Enumeration of all possible log events during to_task processing. Each code
    corresponds to a specific event or error state with predefined message
    templates and log levels.

    The codes are organized by category:
    - Validation codes (INVALID_PROJECT_RESPONSE, NO_DATA_COLLECTION, etc.)
    - Processing codes (ANNOTATING_DATA, ANNOTATION_COMPLETED, etc.)
    - Error codes (CRITICAL_ERROR, TASK_PROCESSING_FAILED, etc.)
    - Inference codes (ANNOTATING_INFERENCE_DATA, INFERENCE_PROCESSING_FAILED, etc.)
    """

    INVALID_PROJECT_RESPONSE = 'INVALID_PROJECT_RESPONSE'
    NO_DATA_COLLECTION = 'NO_DATA_COLLECTION'
    INVALID_DATA_COLLECTION_RESPONSE = 'INVALID_DATA_COLLECTION_RESPONSE'
    NO_TASKS_FOUND = 'NO_TASKS_FOUND'
    TARGET_SPEC_REQUIRED = 'TARGET_SPEC_REQUIRED'
    TARGET_SPEC_NOT_FOUND = 'TARGET_SPEC_NOT_FOUND'
    UNSUPPORTED_METHOD = 'UNSUPPORTED_METHOD'
    ANNOTATING_DATA = 'ANNOTATING_DATA'
    CRITICAL_ERROR = 'CRITICAL_ERROR'
    TASK_PROCESSING_FAILED = 'TASK_PROCESSING_FAILED'
    ANNOTATION_COMPLETED = 'ANNOTATION_COMPLETED'
    INVALID_TASK_RESPONSE = 'INVALID_TASK_RESPONSE'
    TARGET_SPEC_REQUIRED_FOR_TASK = 'TARGET_SPEC_REQUIRED_FOR_TASK'
    UNSUPPORTED_METHOD_FOR_TASK = 'UNSUPPORTED_METHOD_FOR_TASK'
    PRIMARY_IMAGE_URL_NOT_FOUND = 'PRIMARY_IMAGE_URL_NOT_FOUND'
    FILE_SPEC_NOT_FOUND = 'FILE_SPEC_NOT_FOUND'
    FILE_ORIGINAL_NAME_NOT_FOUND = 'FILE_ORIGINAL_NAME_NOT_FOUND'
    URL_NOT_FOUND = 'URL_NOT_FOUND'
    FETCH_DATA_FAILED = 'FETCH_DATA_FAILED'
    CONVERT_DATA_FAILED = 'CONVERT_DATA_FAILED'
    PREPROCESSOR_ID_REQUIRED = 'PREPROCESSOR_ID_REQUIRED'
    INFERENCE_PROCESSING_FAILED = 'INFERENCE_PROCESSING_FAILED'
    ANNOTATING_INFERENCE_DATA = 'ANNOTATING_INFERENCE_DATA'
    INFERENCE_ANNOTATION_COMPLETED = 'INFERENCE_ANNOTATION_COMPLETED'
    INFERENCE_PREPROCESSOR_FAILED = 'INFERENCE_PREPROCESSOR_FAILED'

    # Orchestrator workflow codes
    TO_TASK_STARTED = 'TO_TASK_STARTED'
    TO_TASK_COMPLETED = 'TO_TASK_COMPLETED'
    TO_TASK_FAILED = 'TO_TASK_FAILED'
    STEP_STARTED = 'STEP_STARTED'
    STEP_COMPLETED = 'STEP_COMPLETED'
    STEP_FAILED = 'STEP_FAILED'
    ROLLBACK_FAILED = 'ROLLBACK_FAILED'
    ROLLBACK_ACTION_FAILED = 'ROLLBACK_ACTION_FAILED'

    # Additional strategy codes
    VALIDATION_FAILED = 'VALIDATION_FAILED'
    NO_DATA_UNIT = 'NO_DATA_UNIT'
    NO_DATA_UNIT_FILES = 'NO_DATA_UNIT_FILES'
    TARGET_SPEC_URL_NOT_FOUND = 'TARGET_SPEC_URL_NOT_FOUND'
    DATA_DOWNLOAD_FAILED = 'DATA_DOWNLOAD_FAILED'
    JSON_DECODE_FAILED = 'JSON_DECODE_FAILED'
    ANNOTATION_SUBMISSION_FAILED = 'ANNOTATION_SUBMISSION_FAILED'
    NO_PREPROCESSOR_ID = 'NO_PREPROCESSOR_ID'
    DATA_EXTRACTION_FAILED = 'DATA_EXTRACTION_FAILED'
    PROGRESS_UPDATE_FAILED = 'PROGRESS_UPDATE_FAILED'
    METRICS_RECORDING_FAILED = 'METRICS_RECORDING_FAILED'
    METRICS_UPDATE_FAILED = 'METRICS_UPDATE_FAILED'
    METRICS_FINALIZATION_FAILED = 'METRICS_FINALIZATION_FAILED'


LOG_MESSAGES = {
    LogCode.INVALID_PROJECT_RESPONSE: {
        'message': 'Invalid project response received.',
        'level': Context.DANGER,
    },
    LogCode.NO_DATA_COLLECTION: {
        'message': 'Project does not have a data collection.',
        'level': Context.DANGER,
    },
    LogCode.INVALID_DATA_COLLECTION_RESPONSE: {
        'message': 'Invalid data collection response received.',
        'level': Context.DANGER,
    },
    LogCode.NO_TASKS_FOUND: {
        'message': 'Tasks to annotate not found.',
        'level': Context.WARNING,
    },
    LogCode.TARGET_SPEC_REQUIRED: {
        'message': 'Target specification name is required for file annotation method.',
        'level': Context.DANGER,
    },
    LogCode.TARGET_SPEC_NOT_FOUND: {
        'message': 'Target specification name "{}" not found in file specifications',
        'level': Context.DANGER,
    },
    LogCode.UNSUPPORTED_METHOD: {
        'message': 'Unsupported annotation method: {}',
        'level': Context.DANGER,
    },
    LogCode.ANNOTATING_DATA: {
        'message': 'Annotating data to tasks...',
        'level': None,
    },
    LogCode.CRITICAL_ERROR: {
        'message': 'Critical error occured while processing task. Stopping the job.',
        'level': Context.DANGER,
    },
    LogCode.TASK_PROCESSING_FAILED: {
        'message': 'Failed to process task {}: {}',
        'level': Context.DANGER,
    },
    LogCode.ANNOTATION_COMPLETED: {
        'message': 'Annotation completed. Success: {}, Failed: {}',
        'level': None,
    },
    LogCode.INVALID_TASK_RESPONSE: {
        'message': 'Invalid task response received for task {}',
        'level': Context.DANGER,
    },
    LogCode.TARGET_SPEC_REQUIRED_FOR_TASK: {
        'message': 'Target specification name is required for file annotation method for task {}',
        'level': Context.DANGER,
    },
    LogCode.UNSUPPORTED_METHOD_FOR_TASK: {
        'message': 'Unsupported annotation method: {} for task {}',
        'level': Context.DANGER,
    },
    LogCode.PRIMARY_IMAGE_URL_NOT_FOUND: {
        'message': 'Primary image URL not found in task data for task {}',
        'level': Context.DANGER,
    },
    LogCode.FILE_SPEC_NOT_FOUND: {
        'message': 'File specification not found for task {}',
        'level': Context.DANGER,
    },
    LogCode.FILE_ORIGINAL_NAME_NOT_FOUND: {
        'message': 'File original name not found for task {}',
        'level': Context.DANGER,
    },
    LogCode.URL_NOT_FOUND: {
        'message': 'URL not found for task {}',
        'level': Context.DANGER,
    },
    LogCode.FETCH_DATA_FAILED: {
        'message': 'Failed to fetch data from URL: {} for task {}',
        'level': Context.DANGER,
    },
    LogCode.CONVERT_DATA_FAILED: {
        'message': 'Failed to convert data to task object: {} for task {}',
        'level': Context.DANGER,
    },
    LogCode.PREPROCESSOR_ID_REQUIRED: {
        'message': 'Pre-processor ID is required for inference annotation method for task {}',
        'level': Context.DANGER,
    },
    LogCode.INFERENCE_PROCESSING_FAILED: {
        'message': 'Failed to process inference for task {}: {}',
        'level': Context.DANGER,
    },
    LogCode.ANNOTATING_INFERENCE_DATA: {
        'message': 'Annotating data to tasks using inference...',
        'level': None,
    },
    LogCode.INFERENCE_ANNOTATION_COMPLETED: {
        'message': 'Inference annotation completed. Success: {}, Failed: {}',
        'level': None,
    },
    LogCode.INFERENCE_PREPROCESSOR_FAILED: {
        'message': 'Inference pre processor failed for task {}: {}',
        'level': Context.DANGER,
    },
    # Orchestrator workflow messages
    LogCode.TO_TASK_STARTED: {
        'message': 'ToTask action started.',
        'level': Context.INFO,
    },
    LogCode.TO_TASK_COMPLETED: {
        'message': 'ToTask action completed successfully.',
        'level': Context.SUCCESS,
    },
    LogCode.TO_TASK_FAILED: {
        'message': 'ToTask action failed: {}',
        'level': Context.DANGER,
    },
    LogCode.STEP_STARTED: {
        'message': 'Starting workflow step: {}',
        'level': Context.INFO,
    },
    LogCode.STEP_COMPLETED: {
        'message': 'Completed workflow step: {}',
        'level': Context.INFO,
    },
    LogCode.STEP_FAILED: {
        'message': 'Failed workflow step {}: {}',
        'level': Context.DANGER,
    },
    LogCode.ROLLBACK_FAILED: {
        'message': 'Failed to rollback step {}: {}',
        'level': Context.WARNING,
    },
    LogCode.ROLLBACK_ACTION_FAILED: {
        'message': 'Failed to execute rollback action: {}',
        'level': Context.WARNING,
    },
    # Additional strategy messages
    LogCode.VALIDATION_FAILED: {
        'message': 'Validation failed: {}',
        'level': Context.DANGER,
    },
    LogCode.NO_DATA_UNIT: {
        'message': 'Task does not have a data unit',
        'level': Context.DANGER,
    },
    LogCode.NO_DATA_UNIT_FILES: {
        'message': 'Data unit does not have files',
        'level': Context.DANGER,
    },
    LogCode.TARGET_SPEC_URL_NOT_FOUND: {
        'message': 'Target specification URL not found for {} in task {}',
        'level': Context.DANGER,
    },
    LogCode.DATA_DOWNLOAD_FAILED: {
        'message': 'Failed to download data for task {}: {}',
        'level': Context.DANGER,
    },
    LogCode.JSON_DECODE_FAILED: {
        'message': 'Failed to decode JSON data for task {}: {}',
        'level': Context.DANGER,
    },
    LogCode.ANNOTATION_SUBMISSION_FAILED: {
        'message': 'Failed to submit annotation data for task {}: {}',
        'level': Context.DANGER,
    },
    LogCode.NO_PREPROCESSOR_ID: {
        'message': 'Pre-processor ID is required for inference annotation method',
        'level': Context.DANGER,
    },
    LogCode.DATA_EXTRACTION_FAILED: {
        'message': 'Data extraction failed: {}',
        'level': Context.DANGER,
    },
    LogCode.PROGRESS_UPDATE_FAILED: {
        'message': 'Progress update failed: {}',
        'level': Context.WARNING,
    },
    LogCode.METRICS_RECORDING_FAILED: {
        'message': 'Metrics recording failed: {}',
        'level': Context.WARNING,
    },
    LogCode.METRICS_UPDATE_FAILED: {
        'message': 'Metrics update failed: {}',
        'level': Context.WARNING,
    },
    LogCode.METRICS_FINALIZATION_FAILED: {
        'message': 'Metrics finalization failed: {}',
        'level': Context.WARNING,
    },
}
