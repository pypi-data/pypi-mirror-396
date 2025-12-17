from synapse_sdk.plugins.exceptions import ActionError

from ..context import StepResult, UploadContext
from ..enums import LogCode, UploadStatus
from ..strategies.base import UploadConfig
from .base import BaseStep


class UploadFilesStep(BaseStep):
    """Upload organized files using upload strategy."""

    @property
    def name(self) -> str:
        return 'upload_files'

    @property
    def progress_weight(self) -> float:
        return 0.30

    def execute(self, context: UploadContext) -> StepResult:
        """Execute file upload step."""
        upload_strategy = context.strategies.get('upload')
        if not upload_strategy:
            return self.create_error_result('Upload strategy not found')

        if not context.organized_files:
            context.run.log_message_with_code(LogCode.NO_FILES_UPLOADED)
            return self.create_error_result('No organized files to upload')

        try:
            # Setup progress tracking
            organized_files_count = len(context.organized_files)
            context.run.set_progress(0, organized_files_count, category='upload_data_files')
            context.run.log_message_with_code(LogCode.UPLOADING_DATA_FILES)

            # Initialize metrics
            initial_metrics = {'stand_by': organized_files_count, 'success': 0, 'failed': 0}
            context.update_metrics('data_files', initial_metrics)
            context.run.set_metrics(initial_metrics, category='data_files')

            # Create upload configuration
            # Note: Always uses synchronous upload to guarantee file order
            upload_config = UploadConfig(
                chunked_threshold_mb=context.get_param('max_file_size_mb', 50),
                batch_size=context.get_param('upload_batch_size', 1),
            )

            # Execute upload using strategy
            uploaded_files = upload_strategy.upload(context.organized_files, upload_config)

            # Update context and metrics
            context.add_uploaded_files(uploaded_files)

            # Log upload results
            for uploaded_file in uploaded_files:
                context.run.log_data_file(uploaded_file, UploadStatus.SUCCESS)

            # Update final metrics
            final_metrics = {
                'stand_by': 0,
                'success': len(uploaded_files),
                'failed': organized_files_count - len(uploaded_files),
            }
            context.update_metrics('data_files', final_metrics)
            context.run.set_metrics(final_metrics, category='data_files')

            # Handle success vs failure cases
            if uploaded_files:
                # Success: Set completion progress with elapsed time
                context.run.set_progress(organized_files_count, organized_files_count, category='upload_data_files')
                return self.create_success_result(
                    data={'uploaded_files': uploaded_files},
                    rollback_data={'uploaded_files_count': len(uploaded_files)},
                )
            else:
                # Failure: Mark as failed with elapsed time but no completion
                context.run.set_progress_failed(category='upload_data_files')
                return self.create_error_result('No files were successfully uploaded')

        except Exception as e:
            # Exception: Mark as failed with elapsed time
            context.run.set_progress_failed(category='upload_data_files')
            context.run.log_message_with_code(LogCode.FILE_UPLOAD_FAILED, str(e))
            return self.create_error_result(f'File upload failed: {str(e)}')

    def can_skip(self, context: UploadContext) -> bool:
        """File upload cannot be skipped."""
        return False

    def rollback(self, context: UploadContext) -> None:
        """Rollback file upload."""
        # In a real implementation, this would delete uploaded files
        # For now, just clear the uploaded files list and log
        context.uploaded_files.clear()
        context.run.log_message_with_code(LogCode.ROLLBACK_FILE_UPLOADS)

    def validate_prerequisites(self, context: UploadContext) -> None:
        """Validate prerequisites for file upload."""
        if not context.organized_files:
            raise ValueError('No organized files available for upload')

        collection_id = context.get_param('data_collection')
        if collection_id is None:
            raise ActionError('Data collection parameter is required for upload')
