from ..context import StepResult, UploadContext
from ..enums import LogCode
from .base import BaseStep


class ValidateFilesStep(BaseStep):
    """Validate organized files against specifications."""

    @property
    def name(self) -> str:
        return 'validate_files'

    @property
    def progress_weight(self) -> float:
        return 0.10

    def execute(self, context: UploadContext) -> StepResult:
        """Execute file validation step.

        Validates organized files against specifications using validation strategy.

        Args:
            context (UploadContext): Upload workflow context containing organized files,
                specifications, and strategies.

        Returns:
            StepResult: Success result with validation status, or error result if validation fails.
        """
        validation_strategy = context.strategies.get('validation')
        if not validation_strategy:
            return self.create_error_result('Validation strategy not found')

        if not context.organized_files:
            context.run.log_message_with_code(LogCode.NO_FILES_FOUND)
            return self.create_error_result('No organized files to validate')

        if not context.file_specifications:
            return self.create_error_result('File specifications not available')

        try:
            # Validate organized files against specifications using strategy
            validation_result = validation_strategy.validate_files(context.organized_files, context.file_specifications)

            if not validation_result.valid:
                context.run.log_message_with_code(LogCode.VALIDATION_FAILED)
                error_msg = f'File validation failed: {", ".join(validation_result.errors)}'
                return self.create_error_result(error_msg)

            return self.create_success_result(
                data={'validation_passed': True}, rollback_data={'validated_files_count': len(context.organized_files)}
            )

        except Exception as e:
            return self.create_error_result(f'File validation failed: {str(e)}')

    def can_skip(self, context: UploadContext) -> bool:
        """File validation cannot be skipped."""
        return False

    def rollback(self, context: UploadContext) -> None:
        """Rollback file validation."""
        # Nothing specific to rollback for validation
        context.run.log_message_with_code(LogCode.ROLLBACK_FILE_VALIDATION)

    def validate_prerequisites(self, context: UploadContext) -> None:
        """Validate prerequisites for file validation."""
        if not context.organized_files:
            raise ValueError('No organized files available for validation')

        if not context.file_specifications:
            raise ValueError('File specifications not available for validation')
