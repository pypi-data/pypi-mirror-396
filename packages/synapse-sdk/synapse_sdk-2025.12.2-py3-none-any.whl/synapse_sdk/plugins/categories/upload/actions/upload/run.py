import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from synapse_sdk.plugins.models import Run
from synapse_sdk.shared.enums import Context

from .enums import LOG_MESSAGES, LogCode, UploadStatus
from .utils import PathAwareJSONEncoder


class UploadRun(Run):
    """Upload-specific run management class.

    Extends the base Run class with upload-specific logging capabilities
    and event tracking. Provides type-safe logging using LogCode enums
    and specialized methods for tracking upload progress.

    Manages logging for upload events, data files, data units, and tasks
    throughout the upload lifecycle. Each log entry includes status,
    timestamps, and relevant metadata.

    Attributes:
        Inherits all attributes from base Run class plus upload-specific
        logging methods and nested model classes for structured logging.

    Example:
        >>> run = UploadRun(job_id, context)
        >>> run.log_message_with_code(LogCode.UPLOAD_STARTED)
        >>> run.log_upload_event(LogCode.FILES_DISCOVERED, file_count)
    """

    class UploadEventLog(BaseModel):
        """Model for upload event log entries.

        Records significant events during upload processing with
        status information and timestamps.

        Attributes:
            info (str | None): Optional additional information
            status (Context): Event status/severity level
            created (str): Timestamp when event occurred
        """

        info: Optional[str] = None
        status: Context
        created: str

    class DataFileLog(BaseModel):
        """Model for data file processing log entries.

        Tracks the processing status of individual data files
        during upload operations.

        Attributes:
            data_file_info (str | None): Information about the data file
            status (UploadStatus): Processing status (SUCCESS/FAILED)
            created (str): Timestamp when log entry was created
        """

        data_file_info: str | None
        status: UploadStatus
        created: str

    class DataUnitLog(BaseModel):
        """Model for data unit creation log entries.

        Records the creation status of data units generated from
        uploaded files, including metadata and identifiers.

        Attributes:
            data_unit_id (int | None): ID of created data unit
            status (UploadStatus): Creation status (SUCCESS/FAILED)
            created (str): Timestamp when log entry was created
            data_unit_meta (dict | None): Metadata associated with data unit
        """

        data_unit_id: int | None
        status: UploadStatus
        created: str
        data_unit_meta: dict | None

    class TaskLog(BaseModel):
        """Model for task execution log entries.

        Tracks the execution status of background tasks related
        to upload processing.

        Attributes:
            task_id (int | None): ID of the executed task
            status (UploadStatus): Task execution status (SUCCESS/FAILED)
            created (str): Timestamp when log entry was created
        """

        task_id: int | None
        status: UploadStatus
        created: str

    class MetricsRecord(BaseModel):
        """Model for upload metrics tracking.

        Records count-based metrics for monitoring upload
        progress and success rates.

        Attributes:
            stand_by (int): Number of items waiting to be processed
            failed (int): Number of items that failed processing
            success (int): Number of items successfully processed
        """

        stand_by: int
        failed: int
        success: int

    def log_message_with_code(self, code: LogCode, *args, level: Optional[Context] = None):
        if code not in LOG_MESSAGES:
            # Use direct log_message to avoid recursion
            self.log_message(f'Unknown log code: {code}')
            return

        log_config = LOG_MESSAGES[code]
        message = log_config['message'].format(*args) if args else log_config['message']
        log_level = level or log_config['level'] or Context.INFO

        # Always call log_message for basic logging
        if log_level:
            self.log_message(message, context=log_level.value)
        else:
            self.log_message(message)

    def log_upload_event(self, code: LogCode, *args, level: Optional[Context] = None):
        # Call log_message_with_code to handle the basic logging
        self.log_message_with_code(code, *args, level=level)

        # Also log the event for upload-specific tracking
        if code not in LOG_MESSAGES:
            now = datetime.now().isoformat()
            self.log(
                'upload_event',
                self.UploadEventLog(info=f'Unknown log code: {code}', status=Context.DANGER, created=now).model_dump(),
            )
            return

        log_config = LOG_MESSAGES[code]
        message = log_config['message'].format(*args) if args else log_config['message']
        log_level = level or log_config['level'] or Context.INFO

        now = datetime.now().isoformat()
        self.log(
            'upload_event',
            self.UploadEventLog(info=message, status=log_level, created=now).model_dump(),
        )

    def log_data_file(self, data_file_info: dict, status: UploadStatus):
        now = datetime.now().isoformat()
        data_file_info_str = json.dumps(data_file_info, ensure_ascii=False, cls=PathAwareJSONEncoder)
        self.log(
            'upload_data_file',
            self.DataFileLog(data_file_info=data_file_info_str, status=status, created=now).model_dump(),
        )

    def log_data_unit(self, data_unit_id: int, status: UploadStatus, data_unit_meta: dict | None = None):
        now = datetime.now().isoformat()
        self.log(
            'upload_data_unit',
            self.DataUnitLog(
                data_unit_id=data_unit_id, status=status, created=now, data_unit_meta=data_unit_meta
            ).model_dump(),
        )

    def log_task(self, task_id: int, status: UploadStatus):
        now = datetime.now().isoformat()
        self.log('upload_task', self.TaskLog(task_id=task_id, status=status, created=now).model_dump())

    def log_metrics(self, record: MetricsRecord, category: str):
        record = self.MetricsRecord.model_validate(record)
        self.set_metrics(value=record.model_dump(), category=category)
