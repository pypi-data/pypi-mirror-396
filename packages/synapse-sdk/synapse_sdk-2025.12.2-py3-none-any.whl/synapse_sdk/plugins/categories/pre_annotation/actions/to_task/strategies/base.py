"""Abstract base classes for ToTask strategies."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from synapse_sdk.clients.backend import BackendClient

from ..enums import AnnotationMethod
from ..models import MetricsRecord


class ToTaskContext:
    """Shared context for ToTask action execution."""

    def __init__(
        self,
        params: Dict[str, Any],
        client: BackendClient,
        logger: Any,
        entrypoint: Any = None,
        config: Optional[Dict[str, Any]] = None,
        plugin_config: Optional[Dict[str, Any]] = None,
        job_id: Optional[str] = None,
        progress_categories: Optional[Dict[str, Any]] = None,
        metrics_categories: Optional[Dict[str, Any]] = None,
        project: Optional[Dict[str, Any]] = None,
        data_collection: Optional[Dict[str, Any]] = None,
        task_ids: Optional[List[int]] = None,
        metrics: Optional[MetricsRecord] = None,
        annotation_method: Optional[AnnotationMethod] = None,
    ):
        self.params = params
        self.client = client
        self.logger = logger
        self.entrypoint = entrypoint
        self.config = config
        self.plugin_config = plugin_config
        self.job_id = job_id
        self.progress_categories = progress_categories
        self.metrics_categories = metrics_categories
        self.project = project
        self.data_collection = data_collection
        self.task_ids = task_ids or []
        self.metrics = metrics or MetricsRecord(stand_by=0, failed=0, success=0)
        self.annotation_method = annotation_method
        self.temp_files: List[str] = []
        self.rollback_actions: List[callable] = []

    def add_temp_file(self, file_path: str):
        """Track temporary files for cleanup."""
        self.temp_files.append(file_path)

    def add_rollback_action(self, action: callable):
        """Add rollback action for error recovery."""
        self.rollback_actions.append(action)

    def update_metrics(self, success_count: int, failed_count: int, total_count: int):
        """Update execution metrics."""
        self.metrics = MetricsRecord(
            stand_by=total_count - success_count - failed_count, failed=failed_count, success=success_count
        )


class ValidationStrategy(ABC):
    """Abstract base class for validation strategies."""

    @abstractmethod
    def validate(self, context: ToTaskContext) -> Dict[str, Any]:
        """Validate specific aspects of the ToTask execution.

        Args:
            context: Shared context for the action execution

        Returns:
            Dict with 'success' boolean and optional 'error' message
        """
        pass


class AnnotationStrategy(ABC):
    """Abstract base class for annotation strategies."""

    @abstractmethod
    def process_task(self, context: ToTaskContext, task_id: int, task_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process a single task for annotation.

        Args:
            context: Shared context for the action execution
            task_id: The task ID to process
            task_data: The task data dictionary
            **kwargs: Additional method-specific parameters

        Returns:
            Dict with 'success' boolean and optional 'error' message
        """
        pass


class PreProcessorStrategy(ABC):
    """Abstract base class for pre-processor management strategies."""

    @abstractmethod
    def get_preprocessor_info(self, context: ToTaskContext, preprocessor_id: int) -> Dict[str, Any]:
        """Get pre-processor information.

        Args:
            context: Shared context for the action execution
            preprocessor_id: The pre-processor ID

        Returns:
            Dict with pre-processor info or error
        """
        pass

    @abstractmethod
    def ensure_preprocessor_running(self, context: ToTaskContext, preprocessor_code: str) -> Dict[str, Any]:
        """Ensure pre-processor is running.

        Args:
            context: Shared context for the action execution
            preprocessor_code: The pre-processor code

        Returns:
            Dict indicating success or failure
        """
        pass


class DataExtractionStrategy(ABC):
    """Abstract base class for data extraction strategies."""

    @abstractmethod
    def extract_data(self, context: ToTaskContext, task_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """Extract required data from task.

        Args:
            context: Shared context for the action execution
            task_data: The task data dictionary

        Returns:
            Tuple of extracted data values
        """
        pass


class MetricsStrategy(ABC):
    """Abstract base class for metrics strategies."""

    @abstractmethod
    def update_progress(self, context: ToTaskContext, current: int, total: int):
        """Update progress tracking.

        Args:
            context: Shared context for the action execution
            current: Current progress count
            total: Total items to process
        """
        pass

    @abstractmethod
    def record_task_result(self, context: ToTaskContext, task_id: int, success: bool, error: Optional[str] = None):
        """Record the result of processing a single task.

        Args:
            context: Shared context for the action execution
            task_id: The task ID that was processed
            success: Whether the task processing was successful
            error: Error message if unsuccessful
        """
        pass
