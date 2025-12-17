from synapse_sdk.plugins.exceptions import ActionError
from synapse_sdk.utils.storage import get_pathlib

from ..context import StepResult, UploadContext
from ..enums import LogCode
from .base import BaseStep


class InitializeStep(BaseStep):
    """Initialize upload workflow by setting up storage and paths."""

    @property
    def name(self) -> str:
        return 'initialize'

    @property
    def progress_weight(self) -> float:
        return 0.05

    def execute(self, context: UploadContext) -> StepResult:
        """Execute initialization step."""
        # Get and validate storage
        storage_id = context.get_param('storage')
        if storage_id is None:
            return self.create_error_result('Storage parameter is required')

        try:
            storage = context.client.get_storage(storage_id)
            context.set_storage(storage)
        except Exception as e:
            return self.create_error_result(f'Failed to get storage {storage_id}: {str(e)}')

        # Check if we're in multi-path mode
        use_single_path = context.get_param('use_single_path', True)

        # Get and validate path (only required in single-path mode)
        path = context.get_param('path')
        pathlib_cwd = None

        if use_single_path:
            # Single-path mode: global path is required
            if path is None:
                return self.create_error_result('Path parameter is required in single-path mode')

            try:
                pathlib_cwd = get_pathlib(storage, path)
                context.set_pathlib_cwd(pathlib_cwd)
            except Exception as e:
                return self.create_error_result(f'Failed to get path {path}: {str(e)}')
        else:
            # Multi-path mode: global path is optional (each asset has its own path)
            if path:
                try:
                    pathlib_cwd = get_pathlib(storage, path)
                    context.set_pathlib_cwd(pathlib_cwd)
                except Exception as e:
                    return self.create_error_result(f'Failed to get path {path}: {str(e)}')

        # Return success with rollback data
        rollback_data = {'storage_id': storage_id, 'path': path, 'use_single_path': use_single_path}

        return self.create_success_result(
            data={'storage': storage, 'pathlib_cwd': pathlib_cwd}, rollback_data=rollback_data
        )

    def can_skip(self, context: UploadContext) -> bool:
        """Initialize step cannot be skipped."""
        return False

    def rollback(self, context: UploadContext) -> None:
        """Rollback initialization (cleanup if needed)."""
        # For initialization, there's typically nothing to rollback
        # But we could log the rollback action
        context.run.log_message_with_code(LogCode.ROLLBACK_INITIALIZATION)

    def validate_prerequisites(self, context: UploadContext) -> None:
        """Validate prerequisites for initialization."""
        if context.client is None:
            raise ActionError('Client is required for initialization')

        if context.run is None:
            raise ActionError('Run instance is required for initialization')
