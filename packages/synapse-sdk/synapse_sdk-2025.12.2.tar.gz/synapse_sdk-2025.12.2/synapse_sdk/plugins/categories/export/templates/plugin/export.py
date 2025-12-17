from pathlib import Path
from typing import Generator

from . import BaseExporter


class Exporter(BaseExporter):
    """Plugin export action interface for organizing files.

    This class provides a minimal interface for plugin developers to implement
    their own export logic.
    """

    def __init__(self, run, export_items: Generator, path_root: Path, **params):
        """Initialize the plugin export action class.
        Args:
            run: Plugin run object with logging capabilities.
            export_items (generator):
                - data (dict): dm_schema_data information.
                - files (dict): File information. Includes file URL, original file path, metadata, etc.
                - id (int): target ID (ex. assignment id, task id, ground_truth_event id)
            path_root: pathlib object, the path to export
            **params: Additional parameters
                - name (str): The name of the action.
                - description (str | None): The description of the action.
                - storage (int): The storage ID to save the exported data.
                - save_original_file (bool): Whether to save the original file.
                - path (str): The path to save the exported data.
                - target (str): The target source to export data from. (ex. ground_truth, assignment, task)
                - filter (dict): The filter criteria to apply.
                - extra_params (dict | None): Additional parameters for export customization.
                    Example: {"include_metadata": True, "compression": "gzip"}
                - count (int): Total number of results.
                - results (list): List of results fetched through the list API.
                - project_id (int): Project ID.
                - configuration (dict): Project configuration.
        """
        super().__init__(run, export_items, path_root, **params)

    def export(self, export_items=None, results=None, **kwargs) -> dict:
        """Executes the export task using the base class implementation.

        Args:
            export_items: Optional export items to process. If not provided, uses self.export_items.
            results: Optional results data to process alongside export_items.
            **kwargs: Additional parameters for export customization.

        Returns:
            dict: Result
        """
        return super().export(export_items, results, **kwargs)

    def convert_data(self, data):
        """Converts the data."""
        return data

    def before_convert(self, data):
        """Preprocesses the data before conversion."""
        return data

    def after_convert(self, data):
        """Post-processes the data after conversion."""
        return data

    def sample_dev_log(self):
        """Sample development logging examples for plugin developers.

        This method demonstrates various ways to use log_dev_event() for debugging,
        monitoring, and tracking plugin execution. The event_type is automatically
        generated as 'export_dev_log' for export actions and cannot be modified.

        Use Cases:
        1. Process Tracking: Log when important processes start/complete
        2. Error Handling: Capture detailed error information with appropriate severity
        3. Performance Monitoring: Record timing and resource usage
        4. Data Validation: Log validation results and data quality metrics
        5. Debug Information: Track variable states and execution flow

        Examples show different scenarios where development logging is beneficial:
        - Basic process logging with structured data
        - Error logging with exception details and danger level
        - Performance tracking with timing information
        - Validation logging with success/failure status
        """
        # Example 1: Basic Process Tracking
        # Use when: Starting important processes that you want to monitor
        # Benefits: Helps track execution flow and identify bottlenecks
        self.run.log_dev_event(
            'Starting data conversion process',
            {'data_type': 'img', 'data_size': 'unknown', 'conversion_method': 'custom_format'},
        )

        # Example 2: Error Handling with Detailed Information
        # Use when: Catching exceptions that you want to analyze later
        # Benefits: Provides structured error data for debugging and monitoring
        from synapse_sdk.shared.enums import Context

        try:
            # Simulated operation that might fail
            pass
        except Exception as e:
            self.run.log_dev_event(
                f'Data conversion failed: {str(e)}',
                {
                    'error_type': type(e).__name__,
                    'error_details': str(e),
                    'operation': 'data_conversion',
                    'recovery_attempted': False,
                },
                level=Context.DANGER,
            )

        # Example 3: Performance Monitoring
        # Use when: Tracking processing time for optimization
        # Benefits: Identifies performance bottlenecks and optimization opportunities
        import time

        start_time = time.time()
        # Simulated processing work
        time.sleep(0.001)
        processing_time = time.time() - start_time

        self.run.log_dev_event(
            'File processing completed',
            {
                'processing_time_ms': round(processing_time * 1000, 2),
                'files_processed': 1,
                'performance_rating': 'excellent' if processing_time < 0.1 else 'normal',
            },
        )

        # Example 4: Data Validation Logging
        # Use when: Validating data quality or structure
        # Benefits: Helps identify data issues and track validation metrics
        validation_passed = True  # Simulated validation result
        self.run.log_dev_event(
            'Data validation completed',
            {
                'validation_passed': validation_passed,
                'validation_rules': ['format_check', 'required_fields', 'data_types'],
                'data_quality_score': 95.5,
            },
            level=Context.SUCCESS if validation_passed else Context.WARNING,
        )

        # Example 5: Debug Information with Variable States
        # Use when: Debugging complex logic or tracking variable changes
        # Benefits: Provides insight into execution state at specific points
        current_batch_size = 100
        memory_usage = 45.2  # Simulated memory usage in MB

        self.run.log_dev_event(
            'Processing checkpoint reached',
            {
                'current_batch_size': current_batch_size,
                'memory_usage_mb': memory_usage,
                'checkpoint_location': 'after_data_preprocessing',
                'next_operation': 'file_saving',
            },
        )
