"""Validation strategies for ToTask action."""

from typing import Any, Dict

from ..enums import LogCode
from .base import ToTaskContext, ValidationStrategy


class ProjectValidationStrategy(ValidationStrategy):
    """Strategy for validating project and data collection."""

    def validate(self, context: ToTaskContext) -> Dict[str, Any]:
        """Validate project and data collection exist and are accessible.

        Args:
            context: Shared context for the action execution

        Returns:
            Dict with 'success' boolean and optional 'error' message
        """
        try:
            client = context.client
            project_id = context.params['project']

            # Validate project response
            project_response = client.get_project(project_id)
            if isinstance(project_response, str):
                context.logger.log_message_with_code(LogCode.INVALID_PROJECT_RESPONSE)
                return {'success': False, 'error': 'Invalid project response received'}

            project: Dict[str, Any] = project_response
            context.project = project

            # Validate data collection exists
            data_collection_id = project.get('data_collection')
            if not data_collection_id:
                context.logger.log_message_with_code(LogCode.NO_DATA_COLLECTION)
                return {'success': False, 'error': 'Project does not have a data collection'}

            # Validate data collection response
            data_collection_response = client.get_data_collection(data_collection_id)
            if isinstance(data_collection_response, str):
                context.logger.log_message_with_code(LogCode.INVALID_DATA_COLLECTION_RESPONSE)
                return {'success': False, 'error': 'Invalid data collection response received'}

            data_collection: Dict[str, Any] = data_collection_response
            context.data_collection = data_collection

            return {'success': True}

        except Exception as e:
            error_msg = f'Project validation failed: {str(e)}'
            context.logger.log_message_with_code(LogCode.VALIDATION_FAILED, error_msg)
            return {'success': False, 'error': error_msg}


class TaskValidationStrategy(ValidationStrategy):
    """Strategy for validating and discovering tasks."""

    def validate(self, context: ToTaskContext) -> Dict[str, Any]:
        """Discover and validate tasks for processing.

        Args:
            context: Shared context for the action execution

        Returns:
            Dict with 'success' boolean and optional 'error' message
        """
        try:
            client = context.client

            # Build task query parameters
            task_ids_query_params = {
                'project': context.params['project'],
                'fields': 'id',
            }
            if context.params.get('task_filters'):
                task_ids_query_params.update(context.params['task_filters'])

            # Get tasks
            task_ids_generator, task_ids_count = client.list_tasks(params=task_ids_query_params, list_all=True)
            task_ids = [
                int(item.get('id', 0)) for item in task_ids_generator if isinstance(item, dict) and item.get('id')
            ]

            # Validate tasks found
            if not task_ids_count:
                context.logger.log_message_with_code(LogCode.NO_TASKS_FOUND)
                return {'success': False, 'error': 'No tasks found to annotate'}

            context.task_ids = task_ids
            return {'success': True, 'task_count': len(task_ids)}

        except Exception as e:
            error_msg = f'Task validation failed: {str(e)}'
            context.logger.log_message_with_code(LogCode.VALIDATION_FAILED, error_msg)
            return {'success': False, 'error': error_msg}


class TargetSpecificationValidationStrategy(ValidationStrategy):
    """Strategy for validating target specification for file annotation."""

    def validate(self, context: ToTaskContext) -> Dict[str, Any]:
        """Validate target specification exists in file specifications.

        Args:
            context: Shared context for the action execution

        Returns:
            Dict with 'success' boolean and optional 'error' message
        """
        try:
            # Only validate if using FILE annotation method
            from ..enums import AnnotationMethod

            if context.annotation_method != AnnotationMethod.FILE:
                return {'success': True}

            target_specification_name = context.params.get('target_specification_name')
            if not target_specification_name:
                context.logger.log_message_with_code(LogCode.TARGET_SPEC_REQUIRED)
                return {'success': False, 'error': 'Target specification name is required for file annotation method'}

            # Check if target specification exists in file specifications
            if not context.data_collection:
                return {'success': False, 'error': 'Data collection not available for validation'}

            file_specifications = context.data_collection.get('file_specifications', [])
            target_spec_exists = any(spec.get('name') == target_specification_name for spec in file_specifications)

            if not target_spec_exists:
                context.logger.log_message_with_code(LogCode.TARGET_SPEC_NOT_FOUND, target_specification_name)
                return {
                    'success': False,
                    'error': f"Target specification '{target_specification_name}' not found in file specifications",
                }

            return {'success': True}

        except Exception as e:
            error_msg = f'Target specification validation failed: {str(e)}'
            context.logger.log_message_with_code(LogCode.VALIDATION_FAILED, error_msg)
            return {'success': False, 'error': error_msg}
