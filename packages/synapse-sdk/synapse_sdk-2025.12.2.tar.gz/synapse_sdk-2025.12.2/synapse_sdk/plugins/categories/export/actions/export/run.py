import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from synapse_sdk.plugins.models import Run
from synapse_sdk.shared.enums import Context

from .enums import LOG_MESSAGES, ExportStatus, LogCode


class ExportRun(Run):
    """Export-specific run management class.

    Extends the base Run class with export-specific logging capabilities
    and event tracking. Provides type-safe logging using LogCode enums
    and specialized methods for tracking export progress.

    Manages logging for export events, data files, and export targets
    throughout the export lifecycle. Each log entry includes status,
    timestamps, and relevant metadata.

    Attributes:
        Inherits all attributes from base Run class plus export-specific
        logging methods and nested model classes for structured logging.

    Example:
        >>> run = ExportRun(job_id, context)
        >>> run.log_message_with_code(LogCode.EXPORT_STARTED)
        >>> run.log_export_event(LogCode.RESULTS_RETRIEVED, target_id, count)
    """

    class ExportEventLog(BaseModel):
        """Model for export event log entries.

        Records significant events during export processing with
        target identification and status information.

        Attributes:
            target_id (int): The ID of the export target
            info (str | None): Optional additional information
            status (Context): Event status/severity level
            created (str): Timestamp when event occurred
        """

        target_id: int
        info: str | None = None
        status: Context
        created: str

    class DataFileLog(BaseModel):
        """Model for data file export log entries.

        Tracks the export status of individual data files during
        export operations.

        Attributes:
            target_id (int): The ID of the target being exported
            data_file_info (str | None): JSON information about the data file
            status (ExportStatus): Export status (SUCCESS/FAILED/STAND_BY)
            error (str | None): Error message if export failed
            created (str): Timestamp when log entry was created
        """

        target_id: int
        data_file_info: str | None
        status: ExportStatus
        error: str | None = None
        created: str

    class MetricsRecord(BaseModel):
        """Model for export metrics tracking.

        Records count-based metrics for monitoring export
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
        """Log message using predefined code with type safety.

        Args:
            code (LogCode): The log message code
            *args: Arguments to format the message
            level (Context | None): Optional context level override
        """
        if code not in LOG_MESSAGES:
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

    def log_file(
        self, log_type: str, target_id: int, data_file_info: dict, status: ExportStatus, error: str | None = None
    ):
        """Log export file information.

        Args:
            log_type (str): The type of log ('export_data_file' or 'export_original_file').
            target_id (int): The ID of the data file.
            data_file_info (dict): The JSON info of the data file.
            status (ExportStatus): The status of the data file.
            error (str | None): The error message, if any.
        """
        now = datetime.now().isoformat()
        self.log(
            log_type,
            self.DataFileLog(
                target_id=target_id,
                data_file_info=json.dumps(data_file_info),
                status=status.value,
                error=error,
                created=now,
            ).model_dump(),
        )

    def log_export_event(self, code: LogCode, target_id: int, *args, level: Context | None = None):
        """Log export event using predefined code.

        Args:
            code (str): The log message code.
            target_id (int): The ID of the export target.
            *args: Arguments to format the message.
            level (Context | None): Optional context level override.
        """
        # Call log_message_with_code to handle the basic logging
        self.log_message_with_code(code, *args, level=level)

        # Also log the event for export-specific tracking
        if code not in LOG_MESSAGES:
            now = datetime.now().isoformat()
            self.log(
                'export_event',
                self.ExportEventLog(
                    target_id=target_id, info=f'Unknown log code: {code}', status=Context.DANGER, created=now
                ).model_dump(),
            )
            return

        log_config = LOG_MESSAGES[code]
        message = log_config['message'].format(*args) if args else log_config['message']
        log_level = level or log_config['level'] or Context.INFO

        now = datetime.now().isoformat()
        self.log(
            'export_event',
            self.ExportEventLog(info=message, status=log_level, target_id=target_id, created=now).model_dump(),
        )

    def log_metrics(self, record: MetricsRecord, category: str):
        """Log export metrics.

        Args:
            record (MetricsRecord): The metrics record to log.
            category (str): The category of the metrics.
        """
        record = self.MetricsRecord.model_validate(record)
        self.set_metrics(value=record.model_dump(), category=category)

    def export_log_json_file(
        self,
        target_id: int,
        data_file_info: dict,
        status: ExportStatus = ExportStatus.STAND_BY,
        error: str | None = None,
    ):
        """Log export json data file."""
        self.log_file('export_data_file', target_id, data_file_info, status, error)

    def export_log_original_file(
        self,
        target_id: int,
        data_file_info: dict,
        status: ExportStatus = ExportStatus.STAND_BY,
        error: str | None = None,
    ):
        """Log export origin data file."""
        self.log_file('export_original_file', target_id, data_file_info, status, error)
