"""Data extraction strategies for ToTask action."""

from typing import Any, Dict, Optional, Tuple

from .base import DataExtractionStrategy, ToTaskContext


class FileUrlExtractionStrategy(DataExtractionStrategy):
    """Strategy for extracting file URLs from task data."""

    def extract_data(self, context: ToTaskContext, task_data: Dict[str, Any]) -> str | None:
        """Extract primary file URL from task data.

        Args:
            context: Shared context for the action execution
            task_data: The task data dictionary

        Returns:
            str: The primary file URL or None if not found
        """
        try:
            # This implementation follows the original _extract_primary_file_url logic
            data_unit = task_data.get('data_unit')
            if not data_unit:
                return None

            data_unit_files = data_unit.get('files', {})
            if not data_unit_files:
                return None

            # Find primary file URL
            for key in data_unit_files:
                if data_unit_files[key]['is_primary']:
                    return data_unit_files[key]['url']

            return None

        except Exception as e:
            context.logger.log_message_with_code(
                context.logger.LogCode.DATA_EXTRACTION_FAILED
                if hasattr(context.logger, 'LogCode')
                else 'DATA_EXTRACTION_FAILED',
                str(e),
            )
            return None


class InferenceDataExtractionStrategy(DataExtractionStrategy):
    """Strategy for extracting inference data from task data."""

    def extract_data(self, context: ToTaskContext, task_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """Extract data needed for inference processing.

        Args:
            context: Shared context for the action execution
            task_data: The task data dictionary

        Returns:
            Tuple of (primary_file_url, inference_metadata)
        """
        try:
            # Reuse the file URL extraction logic
            file_strategy = FileUrlExtractionStrategy()
            primary_url = file_strategy.extract_data(context, task_data)

            # Extract additional inference-specific metadata
            data_unit = task_data.get('data_unit', {})
            inference_metadata = {
                'data_unit_id': data_unit.get('id'),
                'task_id': task_data.get('id'),
                'additional_params': context.params.get('inference_params', {}),
            }

            return primary_url, str(inference_metadata) if inference_metadata else None

        except Exception as e:
            context.logger.log_message_with_code(
                context.logger.LogCode.DATA_EXTRACTION_FAILED
                if hasattr(context.logger, 'LogCode')
                else 'DATA_EXTRACTION_FAILED',
                str(e),
            )
            return None, None
