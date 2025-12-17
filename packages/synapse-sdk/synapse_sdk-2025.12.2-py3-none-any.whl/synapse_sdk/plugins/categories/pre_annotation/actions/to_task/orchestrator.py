"""Orchestrator for coordinating ToTask action workflow using Facade pattern."""

from typing import Any, Dict

from synapse_sdk.clients.backend.models import JobStatus

from .enums import AnnotationMethod, LogCode
from .exceptions import CriticalError, PreAnnotationToTaskFailed
from .factory import ToTaskStrategyFactory
from .models import ToTaskResult
from .strategies.base import ToTaskContext


class ToTaskOrchestrator:
    """Facade that orchestrates the complete ToTask annotation workflow."""

    def __init__(self, context: ToTaskContext):
        """Initialize orchestrator with context and strategies.

        Args:
            context: Shared context for the action execution
        """
        self.context = context
        self.factory = ToTaskStrategyFactory()
        self.steps_completed = []

        # Initialize strategies
        self.project_validation = self.factory.create_validation_strategy('project')
        self.task_validation = self.factory.create_validation_strategy('task')
        self.target_spec_validation = self.factory.create_validation_strategy('target_spec')
        self.metrics_strategy = self.factory.create_metrics_strategy()

    def execute_workflow(self) -> Dict[str, Any]:
        """Execute the complete ToTask workflow with rollback support.

        Returns:
            Dict containing the workflow result
        """
        try:
            # Step 1: Project and data collection validation
            self._execute_step('project_validation', self._validate_project)

            # Step 2: Task discovery and validation
            self._execute_step('task_validation', self._validate_tasks)

            # Step 3: Determine annotation method
            self._execute_step('method_determination', self._determine_annotation_method)

            # Step 4: Method-specific validation
            self._execute_step('method_validation', self._validate_annotation_method)

            # Step 5: Initialize processing
            self._execute_step('processing_initialization', self._initialize_processing)

            # Step 6: Process all tasks
            self._execute_step('task_processing', self._process_all_tasks)

            # Step 7: Finalize metrics and progress
            self._execute_step('finalization', self._finalize_processing)

            # Return success result
            result = ToTaskResult(status=JobStatus.SUCCEEDED, message='Pre-annotation to task completed successfully')
            return result.model_dump()

        except Exception as e:
            # Mark progress as failed with elapsed time
            self.context.logger.set_progress_failed(category='annotate_task_data')
            self._rollback_completed_steps()
            if isinstance(e, PreAnnotationToTaskFailed):
                raise e
            raise PreAnnotationToTaskFailed(f'Workflow failed at step {len(self.steps_completed)}: {e}')

    def _execute_step(self, step_name: str, step_func: callable):
        """Execute a workflow step with error handling and progress tracking.

        Args:
            step_name: Name of the step for logging
            step_func: Function to execute for this step

        Returns:
            Result of the step function
        """
        self.context.logger.log_message_with_code(LogCode.STEP_STARTED, step_name)

        try:
            result = step_func()
            self.steps_completed.append(step_name)
            self.context.logger.log_message_with_code(LogCode.STEP_COMPLETED, step_name)
            return result
        except Exception as e:
            self.context.logger.log_message_with_code(LogCode.STEP_FAILED, step_name, str(e))
            raise

    def _validate_project(self):
        """Step 1: Validate project and data collection."""
        result = self.project_validation.validate(self.context)
        if not result['success']:
            error_msg = result.get('error', 'Project validation failed')
            raise PreAnnotationToTaskFailed(error_msg)

    def _validate_tasks(self):
        """Step 2: Discover and validate tasks."""
        result = self.task_validation.validate(self.context)
        if not result['success']:
            error_msg = result.get('error', 'Task validation failed')
            raise PreAnnotationToTaskFailed(error_msg)

    def _determine_annotation_method(self):
        """Step 3: Determine annotation method from parameters."""
        method = self.context.params.get('method')
        if method == AnnotationMethod.FILE:
            self.context.annotation_method = AnnotationMethod.FILE
        elif method == AnnotationMethod.INFERENCE:
            self.context.annotation_method = AnnotationMethod.INFERENCE
        else:
            self.context.logger.log_message_with_code(LogCode.UNSUPPORTED_METHOD, method)
            raise PreAnnotationToTaskFailed(f'Unsupported annotation method: {method}')

    def _validate_annotation_method(self):
        """Step 4: Validate method-specific requirements."""
        if self.context.annotation_method == AnnotationMethod.FILE:
            result = self.target_spec_validation.validate(self.context)
            if not result['success']:
                error_msg = result.get('error', 'Target specification validation failed')
                raise PreAnnotationToTaskFailed(error_msg)

    def _initialize_processing(self):
        """Step 5: Initialize processing metrics and progress."""
        total_tasks = len(self.context.task_ids)
        self.context.update_metrics(0, 0, total_tasks)
        self.metrics_strategy.update_progress(self.context, 0, total_tasks)
        self.context.logger.log_message_with_code(LogCode.ANNOTATING_DATA)

    def _process_all_tasks(self):
        """Step 6: Process all tasks using appropriate annotation strategy."""
        annotation_strategy = self.factory.create_annotation_strategy(self.context.annotation_method)

        total_tasks = len(self.context.task_ids)
        success_count = 0
        failed_count = 0
        current_progress = 0

        # Get task parameters
        task_params = {
            'fields': 'id,data,data_unit',
            'expand': 'data_unit',
        }

        # Process each task
        for task_id in self.context.task_ids:
            try:
                # Get task data
                task_response = self.context.client.get_task(task_id, params=task_params)
                if isinstance(task_response, str):
                    error_msg = 'Invalid task response'
                    self.context.logger.log_annotate_task_event(LogCode.INVALID_TASK_RESPONSE, task_id)
                    self.metrics_strategy.record_task_result(self.context, task_id, False, error_msg)
                    failed_count += 1
                    continue

                task_data: Dict[str, Any] = task_response

                # Process task using annotation strategy
                if self.context.annotation_method == AnnotationMethod.FILE:
                    target_spec_name = self.context.params.get('target_specification_name')
                    result = annotation_strategy.process_task(
                        self.context, task_id, task_data, target_specification_name=target_spec_name
                    )
                else:
                    result = annotation_strategy.process_task(self.context, task_id, task_data)

                # Record result
                if result['success']:
                    success_count += 1
                    self.metrics_strategy.record_task_result(self.context, task_id, True)
                else:
                    failed_count += 1
                    error_msg = result.get('error', 'Unknown error')
                    self.metrics_strategy.record_task_result(self.context, task_id, False, error_msg)

                # Update progress
                current_progress += 1
                self.context.update_metrics(success_count, failed_count, total_tasks)
                self.metrics_strategy.update_progress(self.context, current_progress, total_tasks)
                self.metrics_strategy.update_metrics(self.context, total_tasks, success_count, failed_count)

            except CriticalError:
                self.context.logger.log_message_with_code(LogCode.CRITICAL_ERROR)
                raise PreAnnotationToTaskFailed('Critical error occurred during task processing')

            except Exception as e:
                self.context.logger.log_annotate_task_event(LogCode.TASK_PROCESSING_FAILED, task_id, str(e))
                self.metrics_strategy.record_task_result(self.context, task_id, False, str(e))
                failed_count += 1
                current_progress += 1
                self.context.update_metrics(success_count, failed_count, total_tasks)
                self.metrics_strategy.update_progress(self.context, current_progress, total_tasks)
                self.metrics_strategy.update_metrics(self.context, total_tasks, success_count, failed_count)

    def _finalize_processing(self):
        """Step 7: Finalize metrics."""
        # Finalize metrics
        self.metrics_strategy.finalize_metrics(self.context)

    def _rollback_completed_steps(self):
        """Rollback completed steps in reverse order."""
        for step in reversed(self.steps_completed):
            try:
                rollback_method = getattr(self, f'_rollback_{step}', None)
                if rollback_method:
                    rollback_method()
            except Exception as e:
                self.context.logger.log_message_with_code(LogCode.ROLLBACK_FAILED, step, str(e))

        # Execute any additional rollback actions
        for action in reversed(self.context.rollback_actions):
            try:
                action()
            except Exception as e:
                self.context.logger.log_message_with_code(LogCode.ROLLBACK_ACTION_FAILED, str(e))

    def _rollback_project_validation(self):
        """Rollback project validation step."""
        # Clear cached project and data collection data
        self.context.project = None
        self.context.data_collection = None

    def _rollback_task_validation(self):
        """Rollback task validation step."""
        # Clear cached task data
        self.context.task_ids = []

    def _rollback_processing_initialization(self):
        """Rollback processing initialization step."""
        # Reset metrics
        self.context.update_metrics(0, 0, 0)

    def _rollback_task_processing(self):
        """Rollback task processing step."""
        # Clean up any temporary files
        for temp_file in self.context.temp_files:
            try:
                import os

                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass  # Best effort cleanup
