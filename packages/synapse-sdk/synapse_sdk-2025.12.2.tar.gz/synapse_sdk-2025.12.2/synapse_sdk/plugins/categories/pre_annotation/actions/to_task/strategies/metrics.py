"""Metrics and progress tracking strategies for ToTask action."""

from typing import Optional

from ..enums import AnnotateTaskDataStatus, LogCode
from .base import MetricsStrategy, ToTaskContext


class ProgressTrackingStrategy(MetricsStrategy):
    """Strategy for tracking progress and metrics during task processing."""

    def update_progress(self, context: ToTaskContext, current: int, total: int):
        """Update progress tracking.

        Args:
            context: Shared context for the action execution
            current: Current progress count
            total: Total items to process
        """
        try:
            context.logger.set_progress(current, total, category='annotate_task_data')
        except Exception as e:
            context.logger.log_message_with_code(LogCode.PROGRESS_UPDATE_FAILED, str(e))

    def record_task_result(self, context: ToTaskContext, task_id: int, success: bool, error: Optional[str] = None):
        """Record the result of processing a single task.

        Args:
            context: Shared context for the action execution
            task_id: The task ID that was processed
            success: Whether the task processing was successful
            error: Error message if unsuccessful
        """
        try:
            if success:
                status = AnnotateTaskDataStatus.SUCCESS
                log_data = {'task_id': task_id}
            else:
                status = AnnotateTaskDataStatus.FAILED
                log_data = {'task_id': task_id, 'error': error or 'Unknown error'}

            context.logger.log_annotate_task_data(log_data, status)

        except Exception as e:
            context.logger.log_message_with_code(LogCode.METRICS_RECORDING_FAILED, str(e))

    def update_metrics(self, context: ToTaskContext, total_tasks: int, success_count: int, failed_count: int):
        """Update execution metrics.

        Args:
            context: Shared context for the action execution
            total_tasks: Total number of tasks
            success_count: Number of successful tasks
            failed_count: Number of failed tasks
        """
        try:
            stand_by_count = total_tasks - success_count - failed_count
            context.update_metrics(success_count, failed_count, total_tasks)

            # Update metrics in the logger
            metrics_data = {
                'stand_by': stand_by_count,
                'failed': failed_count,
                'success': success_count,
            }
            context.logger.log_metrics(metrics_data, 'annotate_task_data')

        except Exception as e:
            context.logger.log_message_with_code(LogCode.METRICS_UPDATE_FAILED, str(e))

    def finalize_metrics(self, context: ToTaskContext):
        """Finalize metrics at the end of processing.

        Args:
            context: Shared context for the action execution
        """
        try:
            metrics = context.metrics
            total_tasks = len(context.task_ids)

            context.logger.log_message_with_code(LogCode.ANNOTATION_COMPLETED, metrics.success, metrics.failed)

            # Final progress update - only set completion if some tasks succeeded
            if metrics.success > 0:
                # Success: Set completion progress
                self.update_progress(context, total_tasks, total_tasks)
            else:
                # Failure: Mark as failed (all tasks failed)
                context.logger.set_progress_failed(category='annotate_task_data')

        except Exception as e:
            context.logger.log_message_with_code(LogCode.METRICS_FINALIZATION_FAILED, str(e))
