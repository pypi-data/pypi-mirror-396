from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..context import StepResult, UploadContext
from ..enums import LogCode


class BaseStep(ABC):
    """Abstract base class for all workflow steps."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Step name for logging and tracking."""
        pass

    @property
    @abstractmethod
    def progress_weight(self) -> float:
        """Relative weight for progress calculation (0.0 to 1.0)."""
        pass

    @abstractmethod
    def execute(self, context: UploadContext) -> StepResult:
        """Execute the step logic."""
        pass

    @abstractmethod
    def can_skip(self, context: UploadContext) -> bool:
        """Determine if this step can be skipped based on context."""
        pass

    @abstractmethod
    def rollback(self, context: UploadContext) -> None:
        """Rollback changes made by this step."""
        pass

    def validate_prerequisites(self, context: UploadContext) -> None:
        """Validate step prerequisites. Raises exception if not met."""
        pass

    def log_step_start(self, context: UploadContext) -> None:
        """Log step start."""
        context.run.log_message_with_code(LogCode.STEP_STARTING, self.name)

    def log_step_complete(self, context: UploadContext) -> None:
        """Log step completion."""
        context.run.log_message_with_code(LogCode.STEP_COMPLETED, self.name)

    def log_step_skipped(self, context: UploadContext) -> None:
        """Log step skipped."""
        context.run.log_message_with_code(LogCode.STEP_SKIPPED, self.name)

    def log_step_error(self, context: UploadContext, error: str) -> None:
        """Log step error."""
        context.run.log_message_with_code(LogCode.STEP_ERROR, self.name, error)

    def create_success_result(
        self,
        data: Optional[Dict[str, Any]] = None,
        rollback_data: Optional[Dict[str, Any]] = None,
        skipped: bool = False,
    ) -> StepResult:
        """Create a successful step result."""
        rollback_data = rollback_data or {}
        rollback_data['step_name'] = self.name
        return StepResult(success=True, data=data or {}, rollback_data=rollback_data, skipped=skipped)

    def create_error_result(
        self, error: str, rollback_data: Optional[Dict[str, Any]] = None, original_exception: Optional[Exception] = None
    ) -> StepResult:
        """Create an error step result."""
        rollback_data = rollback_data or {}
        rollback_data['step_name'] = self.name
        return StepResult(
            success=False, error=error, rollback_data=rollback_data, original_exception=original_exception
        )

    def safe_execute(self, context: UploadContext) -> StepResult:
        """Execute step with error handling and logging."""
        try:
            self.validate_prerequisites(context)

            if self.can_skip(context):
                self.log_step_skipped(context)
                return self.create_success_result(skipped=True)

            self.log_step_start(context)
            result = self.execute(context)

            if result.success:
                self.log_step_complete(context)
            else:
                self.log_step_error(context, result.error or 'Unknown error')

            return result

        except Exception as e:
            error_msg = f'Exception in step {self.name}: {str(e)}'
            self.log_step_error(context, error_msg)
            return self.create_error_result(error_msg, original_exception=e)

    def __str__(self):
        return f'{self.__class__.__name__}(name={self.name})'

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', weight={self.progress_weight})"
