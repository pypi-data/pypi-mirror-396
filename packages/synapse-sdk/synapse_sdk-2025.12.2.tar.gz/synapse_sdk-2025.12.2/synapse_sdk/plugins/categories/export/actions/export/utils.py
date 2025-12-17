from abc import ABC, abstractmethod
from typing import Any

from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.i18n import gettext as _


class ExportTargetHandler(ABC):
    """
    Abstract base class for handling export targets.

    This class defines the blueprint for export target handlers, requiring the implementation
    of methods to validate filters, retrieve results, and process collections of results.
    """

    @abstractmethod
    def validate_filter(self, value: dict, client: Any):
        """
        Validate filter query params to request original data from api.

        Args:
            value (dict): The filter criteria to validate.
            client (Any): The client used to validate the filter.

        Raises:
            PydanticCustomError: If the filter criteria are invalid.

        Returns:
            dict: The validated filter criteria.
        """
        pass

    @abstractmethod
    def get_results(self, client: Any, filters: dict):
        """
        Retrieve original data from target sources.

        Args:
            client (Any): The client used to retrieve the results.
            filters (dict): The filter criteria to apply.

        Returns:
            tuple: A tuple containing the results and the total count of results.
        """
        pass

    @abstractmethod
    def get_export_item(self, results):
        """
        Providing elements to build export data.

        Args:
            results (list): The results to process.

        Yields:
            generator: A generator that yields processed data items.
        """
        pass


class AssignmentExportTargetHandler(ExportTargetHandler):
    """Handler for assignment target exports.

    Implements ExportTargetHandler interface for assignment-specific
    export operations including validation, data retrieval, and processing.
    """

    def validate_filter(self, value: dict, client: Any):
        if 'project' not in value:
            raise PydanticCustomError('missing_field', _('Project is required for Assignment.'))
        try:
            client.list_assignments(params=value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get Assignment.'))
        return value

    def get_results(self, client: Any, filters: dict):
        return client.list_assignments(params=filters, list_all=True)

    def get_export_item(self, results):
        for result in results:
            yield {
                'data': result['data'],
                'files': result['file'],
                'id': result['id'],
            }


class GroundTruthExportTargetHandler(ExportTargetHandler):
    """Handler for ground truth target exports.

    Implements ExportTargetHandler interface for ground truth dataset
    export operations including validation, data retrieval, and processing.
    """

    def validate_filter(self, value: dict, client: Any):
        if 'ground_truth_dataset_version' not in value:
            raise PydanticCustomError('missing_field', _('Ground Truth dataset version is required.'))
        try:
            client.get_ground_truth_version(value['ground_truth_dataset_version'])
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get Ground Truth dataset version.'))
        return value

    def get_results(self, client: Any, filters: dict):
        filters['ground_truth_dataset_versions'] = filters.pop('ground_truth_dataset_version')
        return client.list_ground_truth_events(params=filters, list_all=True)

    def get_export_item(self, results):
        for result in results:
            files_key = next(iter(result['data_unit']['files']))
            yield {
                'data': result['data'],
                'files': result['data_unit']['files'][files_key],
                'id': result['id'],
            }


class TaskExportTargetHandler(ExportTargetHandler):
    """Handler for task target exports.

    Implements ExportTargetHandler interface for task-specific
    export operations including validation, data retrieval, and processing.
    """

    def validate_filter(self, value: dict, client: Any):
        if 'project' not in value:
            raise PydanticCustomError('missing_field', _('Project is required for Task.'))
        try:
            client.list_tasks(params=value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get Task.'))
        return value

    def get_results(self, client: Any, filters: dict):
        filters['expand'] = ['data_unit', 'assignment', 'workshop']
        return client.list_tasks(params=filters, list_all=True)

    def get_export_item(self, results):
        for result in results:
            files_key = next(iter(result['data_unit']['files']))
            yield {
                'data': result['data'],
                'files': result['data_unit']['files'][files_key],
                'id': result['id'],
            }


class TargetHandlerFactory:
    """Factory class for creating export target handlers.

    Provides a centralized way to create appropriate target handlers
    based on the target type. Supports assignment, ground_truth, and task targets.

    Example:
        >>> handler = TargetHandlerFactory.get_handler('assignment')
        >>> isinstance(handler, AssignmentExportTargetHandler)
        True
    """

    @staticmethod
    def get_handler(target: str) -> ExportTargetHandler:
        """Get the appropriate target handler for the given target type.

        Args:
            target (str): The target type ('assignment', 'ground_truth', 'task')

        Returns:
            ExportTargetHandler: The appropriate handler instance

        Raises:
            ValueError: If the target type is not supported

        Example:
            >>> handler = TargetHandlerFactory.get_handler('assignment')
            >>> handler.validate_filter({'project': 123}, client)
        """
        if target == 'assignment':
            return AssignmentExportTargetHandler()
        elif target == 'ground_truth':
            return GroundTruthExportTargetHandler()
        elif target == 'task':
            return TaskExportTargetHandler()
        else:
            raise ValueError(f'Unknown target: {target}')
