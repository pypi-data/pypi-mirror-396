"""Refactored ToTask action using Strategy and Facade patterns."""

from typing import Dict

from synapse_sdk.clients.backend import BackendClient
from synapse_sdk.clients.backend.models import JobStatus
from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod

from .enums import LogCode
from .exceptions import PreAnnotationToTaskFailed
from .models import ToTaskParams, ToTaskResult
from .orchestrator import ToTaskOrchestrator
from .run import ToTaskRun
from .strategies.base import ToTaskContext


@register_action
class ToTaskAction(Action):
    """ToTask action for pre-annotation data processing using Strategy and Facade patterns.

    This action handles the process of annotating data to tasks in a project. It supports
    two annotation methods: file-based annotation and inference-based annotation.

    The action uses a Strategy pattern to handle different annotation methods and validation
    approaches, coordinated by an Orchestrator (Facade pattern) that manages the complete
    workflow with rollback capabilities.

    File-based annotation fetches data from file URLs specified in task data units,
    downloads and processes JSON data, and updates task data with the processed information.
    It also validates target specification names against file specifications.

    Inference-based annotation uses pre-processor plugins for model inference
    for automatic data annotation.

    Attrs:
        name (str): Action name, set to 'to_task'.
        category (PluginCategory): Plugin category, set to PRE_ANNOTATION.
        method (RunMethod): Execution method, set to JOB.
        run_class (Type[ToTaskRun]): Run class for this action.
        params_model (Type[ToTaskParams]): Parameter validation model.
        progress_categories (Dict): Progress tracking configuration.
        metrics_categories (Set[str]): Metrics categories for this action.

    Note:
        This action requires a valid project with an associated data collection.
        For file-based annotation, the target_specification_name must exist in the
        project's file specifications.

    Raises:
        ValueError: If run instance or parameters are not properly initialized.
        PreAnnotationToTaskFailed: If the annotation workflow fails.
    """

    name = 'to_task'
    category = PluginCategory.PRE_ANNOTATION
    method = RunMethod.JOB
    run_class = ToTaskRun
    params_model = ToTaskParams
    progress_categories = {
        'annotate_task_data': {
            'proportion': 100,
        },
    }
    metrics_categories = {
        'annotate_task_data': {
            'stand_by': 0,
            'failed': 0,
            'success': 0,
        }
    }

    def __init__(self, *args, **kwargs):
        """Initialize the action with orchestrator context."""
        super().__init__(*args, **kwargs)
        self.context = None

    def start(self) -> Dict:
        """Start to_task action using orchestrator facade.

        The action now uses a simplified workflow:
        1. Validate initialization
        2. Create execution context
        3. Execute workflow through orchestrator
        4. Handle results and errors

        Returns:
            dict: Validated result with status and message.
        """
        # Validate initialization
        if not self.run or not self.params:
            result = ToTaskResult(
                status=JobStatus.FAILED, message='Run instance or parameters not properly initialized'
            )
            raise PreAnnotationToTaskFailed(result.message)

        # Type assertions for better IDE support
        assert isinstance(self.run, ToTaskRun)
        assert isinstance(self.run.client, BackendClient)

        # Log action start
        self.run.log_message_with_code(LogCode.TO_TASK_STARTED)

        try:
            # Create execution context
            self.context = ToTaskContext(
                params=self.params,
                client=self.run.client,
                logger=self.run,
                entrypoint=self.entrypoint,
                config=self.config,
                plugin_config=self.plugin_config,
                job_id=self.job_id,
                progress_categories=self.progress_categories,
                metrics_categories=self.metrics_categories,
            )

            # Create and execute orchestrator
            orchestrator = ToTaskOrchestrator(self.context)
            result = orchestrator.execute_workflow()

            # Log successful completion
            self.run.log_message_with_code(LogCode.TO_TASK_COMPLETED)
            return result

        except PreAnnotationToTaskFailed as e:
            # Re-raise pre-annotation specific errors
            self.run.log_message_with_code(LogCode.TO_TASK_FAILED, str(e))
            raise e

        except Exception as e:
            # Handle unexpected errors
            error_msg = f'ToTask action failed: {str(e)}'
            self.run.log_message_with_code(LogCode.TO_TASK_FAILED, error_msg)
            result = ToTaskResult(status=JobStatus.FAILED, message=error_msg)
            raise PreAnnotationToTaskFailed(result.message)
        finally:
            # Always emit completion log so backend can record end time even on failures
            self.run.end_log()

    def get_context(self) -> ToTaskContext:
        """Get the current execution context for testing/debugging.

        Returns:
            ToTaskContext: The current execution context, or None if not initialized.
        """
        return self.context
