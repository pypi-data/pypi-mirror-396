import json
from datetime import datetime
from typing import Any, Dict, Optional

from synapse_sdk.plugins.models import Run
from synapse_sdk.shared.enums import Context

from .enums import LOG_MESSAGES, AnnotateTaskDataStatus, LogCode
from .models import AnnotateTaskDataLog, AnnotateTaskEventLog, MetricsRecord


class ToTaskRun(Run):
    def log_message_with_code(self, code: LogCode, *args, level: Optional[Context] = None):
        """Log message using predefined code and optional level override."""
        if code not in LOG_MESSAGES:
            self.log_message(f'Unknown log code: {code}')
            return

        log_config = LOG_MESSAGES[code]
        message = log_config['message'].format(*args) if args else log_config['message']
        log_level = level or log_config['level']

        if log_level:
            self.log_message(message, context=log_level.value)
        else:
            self.log_message(message, context=Context.INFO.value)

    def log_annotate_task_event(self, code: LogCode, *args, level: Optional[Context] = None):
        """Log annotate task event using predefined code."""
        if code not in LOG_MESSAGES:
            now = datetime.now().isoformat()
            self.log(
                'annotate_task_event',
                AnnotateTaskEventLog(info=f'Unknown log code: {code}', status=Context.DANGER, created=now).model_dump(),
            )
            return

        log_config = LOG_MESSAGES[code]
        message = log_config['message'].format(*args) if args else log_config['message']
        log_level = level or log_config['level'] or Context.INFO

        now = datetime.now().isoformat()
        self.log(
            'annotate_task_event',
            AnnotateTaskEventLog(info=message, status=log_level, created=now).model_dump(),
        )

    def log_annotate_task_data(self, task_info: Dict[str, Any], status: AnnotateTaskDataStatus):
        """Log annotate task data."""
        now = datetime.now().isoformat()
        self.log(
            'annotate_task_data',
            AnnotateTaskDataLog(task_info=json.dumps(task_info), status=status, created=now).model_dump(),
        )

    def log_metrics(self, record: MetricsRecord, category: str):
        """Log FileToTask metrics.

        Args:
            record (MetricsRecord): The metrics record to log.
            category (str): The category of the metrics.
        """
        record = MetricsRecord.model_validate(record)
        self.set_metrics(value=record.model_dump(), category=category)
