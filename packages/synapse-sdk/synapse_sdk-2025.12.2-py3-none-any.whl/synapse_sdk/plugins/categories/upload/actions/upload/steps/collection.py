from synapse_sdk.plugins.exceptions import ActionError

from ..context import StepResult, UploadContext
from ..enums import LogCode
from .base import BaseStep


class AnalyzeCollectionStep(BaseStep):
    """Analyze data collection to get file specifications."""

    @property
    def name(self) -> str:
        return 'analyze_collection'

    @property
    def progress_weight(self) -> float:
        return 0.05

    def execute(self, context: UploadContext) -> StepResult:
        """Execute collection analysis step."""
        collection_id = context.get_param('data_collection')
        if collection_id is None:
            return self.create_error_result('Data collection parameter is required')

        try:
            # Set initial progress
            context.run.set_progress(0, 2, category='analyze_collection')

            # Get collection from client
            collection = context.client.get_data_collection(collection_id)
            context.run.set_progress(1, 2, category='analyze_collection')

            # Extract file specifications
            file_specifications = collection.get('file_specifications', [])
            context.set_file_specifications(file_specifications)

            # Complete progress
            context.run.set_progress(2, 2, category='analyze_collection')

            return self.create_success_result(
                data={'file_specifications': file_specifications}, rollback_data={'collection_id': collection_id}
            )

        except Exception as e:
            return self.create_error_result(f'Failed to analyze collection {collection_id}: {str(e)}')

    def can_skip(self, context: UploadContext) -> bool:
        """Collection analysis cannot be skipped."""
        return False

    def rollback(self, context: UploadContext) -> None:
        """Rollback collection analysis."""
        # Clear file specifications
        context.file_specifications.clear()
        context.run.log_message_with_code(LogCode.ROLLBACK_COLLECTION_ANALYSIS)

    def validate_prerequisites(self, context: UploadContext) -> None:
        """Validate prerequisites for collection analysis."""
        if context.client is None:
            raise ActionError('Client is required for collection analysis')

        if context.get_param('data_collection') is None:
            raise ActionError('Data collection parameter is required')
