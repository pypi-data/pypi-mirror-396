from pathlib import Path

from synapse_sdk.utils.storage import get_pathlib

from ..context import StepResult, UploadContext
from ..enums import LogCode
from ..exceptions import ExcelParsingError, ExcelSecurityError
from .base import BaseStep


class ProcessMetadataStep(BaseStep):
    """Process metadata from Excel files or other sources.

    This step handles Excel metadata file processing, including path resolution,
    file extraction, and validation. Supports multiple path resolution strategies:
    absolute paths, storage-relative paths, and working directory-relative paths.
    """

    @property
    def name(self) -> str:
        return 'process_metadata'

    @property
    def progress_weight(self) -> float:
        return 0.10

    def execute(self, context: UploadContext) -> StepResult:
        """Execute metadata processing step.

        Processes Excel metadata files by resolving the file path, extracting
        metadata, and validating the extracted data. Supports multiple path
        resolution strategies and handles both explicit metadata paths and
        default metadata file discovery.

        Args:
            context: Upload context containing parameters and state information.

        Returns:
            StepResult containing:
                - success: True if metadata processing succeeded
                - data: Dictionary with 'metadata' key containing extracted metadata
                - rollback_data: Dictionary with 'metadata_processed' flag

        Note:
            If no metadata strategy is configured, the step completes successfully
            with empty metadata. If excel_metadata_path is specified but the file
            is not found, the step logs a warning and continues with empty metadata.
        """
        metadata_strategy = context.strategies.get('metadata')
        if not metadata_strategy:
            context.run.log_message_with_code(LogCode.NO_METADATA_STRATEGY)
            return self.create_success_result(data={'metadata': {}})

        excel_metadata = {}
        temp_file_to_cleanup = None

        try:
            # Check if Excel metadata path is specified
            excel_metadata_path_config = context.get_param('excel_metadata_path')

            if excel_metadata_path_config:
                # Path-based approach (only supported method)
                excel_path = self._resolve_excel_path_from_string(excel_metadata_path_config, context)

                if not excel_path or not excel_path.exists():
                    context.run.log_message_with_code(LogCode.EXCEL_FILE_NOT_FOUND_PATH)
                    return self.create_success_result(data={'metadata': {}})

                excel_metadata = metadata_strategy.extract(excel_path)
            else:
                # Look for default metadata files (meta.xlsx, meta.xls)
                # Only possible in single-path mode where pathlib_cwd is set
                if context.pathlib_cwd:
                    excel_path = self._find_excel_metadata_file(context.pathlib_cwd)
                    if excel_path:
                        excel_metadata = metadata_strategy.extract(excel_path)
                else:
                    context.run.log_message_with_code(LogCode.NO_METADATA_STRATEGY)

            # Validate extracted metadata
            if excel_metadata:
                validation_result = metadata_strategy.validate(excel_metadata)
                if not validation_result.valid:
                    error_msg = f'Metadata validation failed: {", ".join(validation_result.errors)}'
                    return self.create_error_result(error_msg)
                context.run.log_message_with_code(LogCode.EXCEL_METADATA_LOADED, len(excel_metadata))

            return self.create_success_result(
                data={'metadata': excel_metadata}, rollback_data={'metadata_processed': len(excel_metadata) > 0}
            )

        except ExcelSecurityError as e:
            context.run.log_message_with_code(LogCode.EXCEL_SECURITY_VIOLATION, str(e))
            return self.create_error_result(f'Excel security violation: {str(e)}')

        except ExcelParsingError as e:
            # If excel_metadata_path was specified, this is an error
            # If we were just looking for default files, it's not an error
            if context.get_param('excel_metadata_path'):
                context.run.log_message_with_code(LogCode.EXCEL_PARSING_ERROR, str(e))
                return self.create_error_result(f'Excel parsing error: {str(e)}')
            else:
                context.run.log_message_with_code(LogCode.EXCEL_PARSING_ERROR, str(e))
                return self.create_success_result(data={'metadata': {}})

        except Exception as e:
            return self.create_error_result(f'Unexpected error processing metadata: {str(e)}')

        finally:
            # Clean up temporary file if it was created from base64
            if temp_file_to_cleanup and temp_file_to_cleanup.exists():
                try:
                    temp_file_to_cleanup.unlink()
                    context.run.log_message_with_code(LogCode.METADATA_TEMP_FILE_CLEANUP, temp_file_to_cleanup)
                except Exception as e:
                    context.run.log_message_with_code(
                        LogCode.METADATA_TEMP_FILE_CLEANUP_FAILED, temp_file_to_cleanup, str(e)
                    )

    def can_skip(self, context: UploadContext) -> bool:
        """Check if metadata step can be skipped.

        Args:
            context: Upload context containing strategy configuration.

        Returns:
            True if no metadata strategy is configured, False otherwise.
        """
        return 'metadata' not in context.strategies

    def rollback(self, context: UploadContext) -> None:
        """Rollback metadata processing.

        Clears any loaded metadata from the context to restore the state
        before this step was executed.

        Args:
            context: Upload context containing metadata to clear.
        """
        # Clear any loaded metadata
        context.metadata.clear()

    def _resolve_excel_path_from_string(self, excel_path_str: str, context: UploadContext) -> Path | None:
        """Resolve Excel metadata path from a string path.

        Attempts to resolve the Excel metadata file path using multiple strategies
        in the following order:
        1. Absolute filesystem path
        2. Relative to storage default path (if storage is available)
        3. Relative to working directory (if pathlib_cwd is set in single-path mode)

        Args:
            excel_path_str: File path string to the Excel metadata file.
            context: Upload context containing storage configuration and working
                directory information for path resolution.

        Returns:
            Path object pointing to the Excel file if found, None otherwise.

        Examples:
            Absolute path:

                >>> path = self._resolve_excel_path_from_string(
                ...     "/data/meta.xlsx", context
                ... )

            Storage-relative path:

                >>> path = self._resolve_excel_path_from_string(
                ...     "metadata/meta.xlsx", context
                ... )

        Note:
            When resolving storage-relative paths, the method logs the resolved
            path for debugging purposes. Failed storage path resolution is logged
            but does not raise an exception.
        """
        # Try absolute path first
        path = Path(excel_path_str)
        if path.exists() and path.is_file():
            return path

        # Try relative to storage default path (if storage is available)
        if context.storage:
            try:
                storage_base_path = get_pathlib(context.storage, excel_path_str)
                if storage_base_path.exists() and storage_base_path.is_file():
                    context.run.log_message_with_code(LogCode.EXCEL_PATH_RESOLVED_STORAGE, str(storage_base_path))
                    return storage_base_path
            except (FileNotFoundError, PermissionError) as e:
                # Expected errors when path doesn't exist or no permissions
                context.run.log_message_with_code(LogCode.EXCEL_PATH_RESOLUTION_FAILED, type(e).__name__, str(e))
            except Exception as e:
                # Unexpected errors should be logged with more detail for debugging
                context.run.log_message_with_code(LogCode.EXCEL_PATH_RESOLUTION_ERROR, type(e).__name__, str(e))

        # Try relative to cwd (only if pathlib_cwd is set - single-path mode)
        if context.pathlib_cwd:
            path = context.pathlib_cwd / excel_path_str
            if path.exists() and path.is_file():
                return path

        # Could not resolve path
        return None

    def _find_excel_metadata_file(self, pathlib_cwd: Path) -> Path:
        """Find default Excel metadata file in working directory.

        Searches for standard Excel metadata filenames (meta.xlsx, meta.xls)
        in the specified working directory. Prioritizes .xlsx format over .xls.

        Args:
            pathlib_cwd: Working directory path to search in. Must not be None.

        Returns:
            Path object to the Excel metadata file if found, None otherwise.

        Note:
            This method only searches the immediate working directory, not
            subdirectories. The search order is: meta.xlsx, then meta.xls.
        """
        if not pathlib_cwd:
            return None

        # Check .xlsx first as it's more common
        excel_path = pathlib_cwd / 'meta.xlsx'
        if excel_path.exists():
            return excel_path

        # Fallback to .xls
        excel_path = pathlib_cwd / 'meta.xls'
        if excel_path.exists():
            return excel_path

        return None
