from typing import Any, Dict

from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.plugins.exceptions import ActionError

from .context import UploadContext
from .enums import LogCode
from .factory import StrategyFactory
from .models import UploadParams
from .orchestrator import UploadOrchestrator
from .registry import StepRegistry
from .run import UploadRun
from .steps.cleanup import CleanupStep
from .steps.collection import AnalyzeCollectionStep
from .steps.generate import GenerateDataUnitsStep
from .steps.initialize import InitializeStep
from .steps.metadata import ProcessMetadataStep
from .steps.organize import OrganizeFilesStep
from .steps.upload import UploadFilesStep
from .steps.validate import ValidateFilesStep
from .utils import ExcelSecurityConfig


@register_action
class UploadAction(Action):
    """Upload action for processing and uploading files to storage.

    This implementation uses Strategy and Facade patterns to provide a clean,
    extensible architecture for upload operations. The monolithic legacy
    implementation has been refactored into pluggable strategies and workflow steps.

    Features:
    - Strategy pattern for pluggable behaviors (validation, file discovery, etc.)
    - Facade pattern with UploadOrchestrator for simplified workflow management
    - Step-based workflow with automatic rollback on failures
    - Comprehensive error handling and progress tracking
    - Easy extensibility for new strategies and workflow steps

    Class Attributes:
        name (str): Action identifier ('upload')
        category (PluginCategory): UPLOAD category
        method (RunMethod): JOB execution method
        run_class (type): UploadRun for specialized logging
        params_model (type): UploadParams for parameter validation
        progress_categories (dict): Progress tracking configuration
        metrics_categories (dict): Metrics collection configuration

    Example:
        >>> action = UploadAction(
        ...     params={
        ...         'name': 'Data Upload',
        ...         'path': '/data/files',
        ...         'storage': 1,
        ...         'data_collection': 5
        ...     },
        ...     plugin_config=config
        ... )
        >>> result = action.start()
    """

    name = 'upload'
    category = PluginCategory.UPLOAD
    method = RunMethod.JOB
    run_class = UploadRun
    params_model = UploadParams
    progress_categories = {
        'analyze_collection': {
            'proportion': 2,
        },
        'upload_data_files': {
            'proportion': 38,
        },
        'generate_data_units': {
            'proportion': 60,
        },
    }
    metrics_categories = {
        'data_files': {
            'stand_by': 0,
            'failed': 0,
            'success': 0,
        },
        'data_units': {
            'stand_by': 0,
            'failed': 0,
            'success': 0,
        },
    }

    def __init__(self, *args, **kwargs):
        """Initialize the upload action."""
        super().__init__(*args, **kwargs)

        # Initialize Excel configuration from config.yaml
        self.excel_config = ExcelSecurityConfig.from_action_config(self.config)
        self.strategy_factory = StrategyFactory()
        self.step_registry = StepRegistry()
        self._configure_workflow()

    def _configure_workflow(self) -> None:
        """Configure workflow steps based on parameters.

        Registers all workflow steps in the correct order. Steps can be
        dynamically added, removed, or reordered for different use cases.
        """
        # Register steps in execution order
        self.step_registry.register(InitializeStep())
        self.step_registry.register(ProcessMetadataStep())
        self.step_registry.register(AnalyzeCollectionStep())
        self.step_registry.register(OrganizeFilesStep())
        self.step_registry.register(ValidateFilesStep())
        self.step_registry.register(UploadFilesStep())
        self.step_registry.register(GenerateDataUnitsStep())
        self.step_registry.register(CleanupStep())

    def start(self) -> Dict[str, Any]:
        """Execute upload workflow with uploader integration.

        This method integrates the essential uploader mechanism with the new
        strategy pattern architecture while maintaining backward compatibility.

        Returns:
            Dict[str, Any]: Upload result with file counts, success status, and metrics

        Raises:
            ActionError: If upload workflow fails
        """
        try:
            # Ensure params is not None
            params = self.params or {}

            # Create upload context for sharing state between steps
            context = UploadContext(params, self.run, self.client, action=self)

            # Configure strategies based on parameters with context
            strategies = self._configure_strategies(context)

            # Create orchestrator but run it with uploader integration
            orchestrator = UploadOrchestrator(context, self.step_registry, strategies)

            # Execute the workflow steps, but intercept after organize step
            result = self._execute_with_uploader_integration(orchestrator, context)

            return result

        except Exception as e:
            # Log the error and re-raise as ActionError
            if self.run:
                self.run.log_message_with_code(LogCode.UPLOAD_WORKFLOW_FAILED, str(e))
            raise ActionError(f'Upload failed: {str(e)}')
        finally:
            # Always emit completion log so backend can record end time even on failures
            if self.run:
                self.run.end_log()

    def _execute_with_uploader_integration(self, orchestrator, context) -> Dict[str, Any]:
        """Execute workflow with proper uploader integration."""
        # Inject strategies into context before executing steps
        orchestrator._inject_strategies_into_context()

        # Run initial steps up to file organization
        steps = orchestrator.step_registry.get_steps()

        # Execute steps one by one until we reach the organization step
        for i, step in enumerate(steps):
            if step.name in ['initialize', 'process_metadata', 'analyze_collection', 'organize_files']:
                try:
                    result = step.safe_execute(context)
                    context.update(result)
                    if not result.success:
                        raise Exception(f"Step '{step.name}' failed: {result.error}")
                except Exception as e:
                    raise ActionError(f"Failed at step '{step.name}': {str(e)}")

        # Execute remaining steps
        for step in steps:
            if step.name in ['validate_files', 'upload_files', 'generate_data_units', 'cleanup']:
                try:
                    result = step.safe_execute(context)
                    context.update(result)
                    if not result.success:
                        raise Exception(f"Step '{step.name}' failed: {result.error}")
                except Exception as e:
                    raise ActionError(f"Failed at step '{step.name}': {str(e)}")

        # Return the final result from context
        return context.get_result()

    def _configure_strategies(self, context=None) -> Dict[str, Any]:
        """Configure strategies based on parameters.

        Uses the Strategy pattern to create appropriate strategy implementations
        based on the action parameters. This allows for runtime selection of
        different behaviors (recursive vs flat discovery, batch vs single data unit creation, etc.).

        Args:
            context: UploadContext for strategies that need access to client/run

        Returns:
            Dict[str, Any]: Dictionary of strategy instances keyed by type
        """
        # Ensure params is not None
        params = self.params or {}

        return {
            'validation': self.strategy_factory.create_validation_strategy(params, context),
            'file_discovery': self.strategy_factory.create_file_discovery_strategy(params, context),
            'metadata': self.strategy_factory.create_metadata_strategy(params, context),
            'upload': self.strategy_factory.create_upload_strategy(params, context),
            'data_unit': self.strategy_factory.create_data_unit_strategy(params, context),
        }

    def get_uploader(self, path, file_specification, organized_files, params: Dict = {}):
        """Get uploader from entrypoint (compatibility method).

        This method is kept for backward compatibility with existing code
        that may still call it directly.
        """
        return self.entrypoint(
            self.run, path, file_specification, organized_files, extra_params=params.get('extra_params')
        )

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get summary of configured workflow.

        Returns:
            Dict[str, Any]: Summary of steps and strategies
        """
        return {
            'steps': [step.name for step in self.step_registry.get_steps()],
            'step_count': len(self.step_registry),
            'total_progress_weight': self.step_registry.get_total_progress_weight(),
            'available_strategies': self.strategy_factory.get_available_strategies(),
        }
