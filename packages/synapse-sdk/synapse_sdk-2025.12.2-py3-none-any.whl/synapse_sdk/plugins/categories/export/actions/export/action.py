from itertools import tee
from typing import Any, Dict

from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.i18n import gettext as _
from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.utils.storage import get_pathlib

from .enums import LogCode
from .models import ExportParams
from .run import ExportRun
from .utils import TargetHandlerFactory


@register_action
class ExportAction(Action):
    """Main export action for processing and exporting data from various targets.

    Handles export operations including target validation, data retrieval,
    and file generation. Supports export from assignment, ground_truth, and task
    targets with comprehensive progress tracking and error handling.

    Features:
    - Multiple target source support (assignment, ground_truth, task)
    - Filter validation and data retrieval
    - Original file and data file export options
    - Progress tracking with detailed metrics
    - Comprehensive error logging
    - Project configuration handling

    Class Attributes:
        name (str): Action identifier ('export')
        category (PluginCategory): EXPORT category
        method (RunMethod): JOB execution method
        run_class (type): ExportRun for specialized logging
        params_model (type): ExportParams for parameter validation
        progress_categories (dict): Progress tracking configuration
        metrics_categories (dict): Metrics collection configuration

    Example:
        >>> action = ExportAction(
        ...     params={
        ...         'name': 'Assignment Export',
        ...         'storage': 1,
        ...         'path': '/exports/assignments',
        ...         'target': 'assignment',
        ...         'filter': {'project': 123}
        ...     },
        ...     plugin_config=config
        ... )
        >>> result = action.start()
    """

    name = 'export'
    category = PluginCategory.EXPORT
    method = RunMethod.JOB
    params_model = ExportParams
    run_class = ExportRun
    progress_categories = {
        'dataset_conversion': {
            'proportion': 100,
        }
    }
    metrics_categories = {
        'data_file': {
            'stand_by': 0,
            'failed': 0,
            'success': 0,
        },
        'original_file': {
            'stand_by': 0,
            'failed': 0,
            'success': 0,
        },
    }

    def get_filtered_results(self, filters, handler):
        """Get filtered target results.

        Retrieves data from the specified target using the provided filters
        through the appropriate target handler.

        Args:
            filters (dict): Filter criteria to apply
            handler (ExportTargetHandler): Target-specific handler

        Returns:
            tuple: (results, count) where results is the data and count is total

        Raises:
            PydanticCustomError: If data retrieval fails
        """
        try:
            result_list = handler.get_results(self.client, filters)
            results = result_list[0]
            count = result_list[1]
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get dataset.'))
        return results, count

    def start(self) -> Dict[str, Any]:
        """Start the export process.

        Main entry point for export operations. Handles parameter preparation,
        target handler selection, data retrieval, and export execution.

        Returns:
            Dict[str, Any]: Export results from the entrypoint

        Raises:
            Various exceptions based on validation and processing failures
        """
        self.run.log_message_with_code(LogCode.EXPORT_STARTED)

        # Get expand setting from config, default to True (expand data)
        filters = {**self.params['filter']}
        data_expand = self.config.get('data_expand', True)
        if data_expand:
            filters['expand'] = 'data'

        target = self.params['target']
        handler = TargetHandlerFactory.get_handler(target)

        self.params['results'], self.params['count'] = self.get_filtered_results(filters, handler)

        if self.params['count'] == 0:
            self.run.log_message_with_code(LogCode.NO_RESULTS_FOUND)
        else:
            self.run.log_message_with_code(LogCode.RESULTS_RETRIEVED, self.params['count'])

        # For the 'ground_truth' target, retrieve project information from the first result and add configuration
        if target == 'ground_truth':
            try:
                # Split generator into two using tee()
                peek_iter, main_iter = tee(self.params['results'])
                first_result = next(peek_iter)  # Peek first value only
                project_pk = first_result['project']
                project_info = self.client.get_project(project_pk)
                self.params['project_id'] = project_pk
                self.params['configuration'] = project_info.get('configuration', {})
                self.params['results'] = main_iter  # Keep original generator intact
            except (StopIteration, KeyError):
                self.params['configuration'] = {}
        # For the 'assignment' and 'task' targets, retrieve the project from the filter as before
        elif target in ['assignment', 'task'] and 'project' in self.params['filter']:
            project_pk = self.params['filter']['project']
            project_info = self.client.get_project(project_pk)
            self.params['configuration'] = project_info.get('configuration', {})

        export_items = handler.get_export_item(self.params['results'])
        storage = self.client.get_storage(self.params['storage'])
        pathlib_cwd = get_pathlib(storage, self.params['path'])
        exporter = self.entrypoint(self.run, export_items, pathlib_cwd, **self.params)

        try:
            result = exporter.export()
            self.run.log_message_with_code(LogCode.EXPORT_COMPLETED)
            return result
        except Exception as e:
            self.run.log_message_with_code(LogCode.EXPORT_FAILED, str(e))
            raise
