from pathlib import Path
from typing import Any, Dict, List

from ...enums import LogCode, UploadStatus
from ..base import UploadConfig, UploadStrategy


class SyncUploadStrategy(UploadStrategy):
    """Synchronous upload strategy."""

    def __init__(self, context):
        self.context = context

    def upload(self, files: List[Dict], config: UploadConfig) -> List[Dict]:
        """Upload files synchronously.

        Integrates plugin's uploader for file processing before upload.
        """
        # Process files through plugin uploader if available
        processed_files = self._process_files_with_uploader(files)

        uploaded_files = []
        client = self.context.client
        collection_id = self.context.get_param('data_collection')

        for organized_file in processed_files:
            try:
                use_chunked_upload = self._requires_chunked_upload(organized_file, config)
                uploaded_data_file = client.upload_data_file(organized_file, collection_id, use_chunked_upload)
                self.context.run.log_data_file(organized_file, UploadStatus.SUCCESS)
                uploaded_files.append(uploaded_data_file)
            except Exception as e:
                self.context.run.log_data_file(organized_file, UploadStatus.FAILED)
                self.context.run.log_message_with_code(LogCode.FILE_UPLOAD_FAILED, str(e))
                # Continue with other files instead of failing completely

        return uploaded_files

    def _requires_chunked_upload(self, organized_file: Dict[str, Any], config: UploadConfig) -> bool:
        """Determine if chunked upload is required based on file sizes."""
        max_file_size_mb = config.chunked_threshold_mb
        for file_path in organized_file.get('files', {}).values():
            if isinstance(file_path, Path) and self._get_file_size_mb(file_path) > max_file_size_mb:
                return True
        return False

    def _get_file_size_mb(self, file_path: Path) -> float:
        """Get file size in megabytes."""
        return file_path.stat().st_size / (1024 * 1024)

    def _process_files_with_uploader(self, files: List[Dict]) -> List[Dict]:
        """Process files through plugin uploader if available.

        Args:
            files: List of organized files to process

        Returns:
            Processed files (filtered, transformed) ready for upload
        """
        action = self.context._action
        if not (hasattr(action, 'entrypoint') and action.entrypoint):
            # No plugin uploader, return files as-is
            return files

        try:
            use_single_path = self.context.get_param('use_single_path', True)
            pathlib_cwd = self.context.get('pathlib_cwd')
            uploader_path = pathlib_cwd if use_single_path else None

            # Get uploader instance from plugin
            uploader = action.get_uploader(
                path=uploader_path,
                file_specification=self.context.file_specifications,
                organized_files=files,
                params=self.context.params,
            )

            # Process files through uploader (includes extension validation, transformation, etc.)
            return uploader.handle_upload_files()

        except Exception as e:
            self.context.run.log_message_with_code(LogCode.FILE_UPLOAD_FAILED, f'Uploader processing failed: {str(e)}')
            # Return original files if uploader fails
            return files
