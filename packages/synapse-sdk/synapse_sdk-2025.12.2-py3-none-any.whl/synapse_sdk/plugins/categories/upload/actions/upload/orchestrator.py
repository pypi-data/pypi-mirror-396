import traceback
from typing import Any, Dict, List

from .context import UploadContext
from .enums import LogCode
from .registry import StepRegistry
from .steps.base import BaseStep


class UploadOrchestrator:
    """Facade that orchestrates the upload workflow using strategies and steps."""

    def __init__(self, context: UploadContext, step_registry: StepRegistry, strategies: Dict[str, Any]):
        self.context = context
        self.step_registry = step_registry
        self.strategies = strategies
        self.executed_steps: List[BaseStep] = []
        self.current_step_index = 0

    def execute(self) -> Dict[str, Any]:
        """Execute the complete upload workflow."""
        try:
            self._log_workflow_start()
            self._inject_strategies_into_context()

            steps = self.step_registry.get_steps()
            total_steps = len(steps)

            for i, step in enumerate(steps):
                self.current_step_index = i

                try:
                    result = step.safe_execute(self.context)
                    self.context.update(result)

                    if result.success:
                        if not result.skipped:
                            self.executed_steps.append(step)
                        self._update_progress(i + 1, total_steps)
                    else:
                        # Step failed, initiate rollback
                        self._log_step_failure(step, result.error)
                        self._rollback()
                        # Re-raise original exception if available, otherwise create new one
                        if result.original_exception:
                            raise result.original_exception
                        else:
                            raise Exception(f"Step '{step.name}' failed: {result.error}")

                except Exception as e:
                    self._log_step_exception(step, str(e))
                    self._rollback()
                    raise

            self._log_workflow_complete()
            return self.context.get_result()

        except Exception as e:
            self._log_workflow_error(str(e))
            # Ensure rollback is called if not already done
            if not hasattr(self, '_rollback_executed'):
                self._rollback()
            raise

    def _inject_strategies_into_context(self) -> None:
        """Inject strategies into context for steps to use."""
        if not hasattr(self.context, 'strategies'):
            self.context.strategies = {}
        self.context.strategies.update(self.strategies)

    def _rollback(self) -> None:
        """Rollback executed steps in reverse order."""
        if hasattr(self, '_rollback_executed'):
            return  # Prevent multiple rollbacks

        self._rollback_executed = True
        self._log_rollback_start()

        # Rollback in reverse order
        for step in reversed(self.executed_steps):
            try:
                self._log_step_rollback(step)
                step.rollback(self.context)
            except Exception as e:
                # Log rollback error but continue with other steps
                self._log_rollback_error(step, str(e))

        self._log_rollback_complete()

    def _update_progress(self, current_step: int, total_steps: int) -> None:
        """Update overall progress based on step completion."""
        if total_steps == 0:
            return

        # Calculate progress based on step weights
        completed_weight = 0.0
        total_weight = self.step_registry.get_total_progress_weight()

        for i, step in enumerate(self.executed_steps):
            completed_weight += step.progress_weight

        progress_percentage = (completed_weight / total_weight) * 100 if total_weight > 0 else 0

        # Update context with progress information
        self.context.update_metrics(
            'workflow',
            {
                'current_step': current_step,
                'total_steps': total_steps,
                'progress_percentage': progress_percentage,
                'completed_weight': completed_weight,
                'total_weight': total_weight,
            },
        )

    def _log_workflow_start(self) -> None:
        """Log workflow start."""
        steps = self.step_registry.get_steps()
        step_names = [step.name for step in steps]
        self.context.run.log_message_with_code(LogCode.WORKFLOW_STARTING, len(steps), step_names)

    def _log_workflow_complete(self) -> None:
        """Log workflow completion."""
        self.context.run.log_message_with_code(LogCode.WORKFLOW_COMPLETED)

    def _log_workflow_error(self, error: str) -> None:
        """Log workflow error."""
        self.context.run.log_message_with_code(LogCode.WORKFLOW_FAILED, error)

    def _log_step_failure(self, step: BaseStep, error: str) -> None:
        """Log step failure."""
        self.context.run.log_message_with_code(LogCode.STEP_FAILED, step.name, error)

    def _log_step_exception(self, step: BaseStep, error: str) -> None:
        """Log step exception."""
        self.context.run.log_message_with_code(LogCode.STEP_EXCEPTION, step.name, error)
        # Log full traceback for debugging
        self.context.run.log_message_with_code(LogCode.STEP_TRACEBACK, traceback.format_exc())

    def _log_rollback_start(self) -> None:
        """Log rollback start."""
        self.context.run.log_message_with_code(LogCode.ROLLBACK_STARTING, len(self.executed_steps))

    def _log_rollback_complete(self) -> None:
        """Log rollback completion."""
        self.context.run.log_message_with_code(LogCode.ROLLBACK_COMPLETED)

    def _log_step_rollback(self, step: BaseStep) -> None:
        """Log step rollback."""
        self.context.run.log_message_with_code(LogCode.STEP_ROLLBACK, step.name)

    def _log_rollback_error(self, step: BaseStep, error: str) -> None:
        """Log rollback error."""
        self.context.run.log_message_with_code(LogCode.ROLLBACK_ERROR, step.name, error)

    def get_executed_steps(self) -> List[BaseStep]:
        """Get list of successfully executed steps."""
        return self.executed_steps.copy()

    def get_current_step_index(self) -> int:
        """Get current step index."""
        return self.current_step_index

    def get_total_steps(self) -> int:
        """Get total number of steps."""
        return len(self.step_registry.get_steps())

    def is_rollback_executed(self) -> bool:
        """Check if rollback has been executed."""
        return hasattr(self, '_rollback_executed')

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get workflow execution summary."""
        steps = self.step_registry.get_steps()
        return {
            'total_steps': len(steps),
            'executed_steps': len(self.executed_steps),
            'current_step_index': self.current_step_index,
            'step_names': [step.name for step in steps],
            'executed_step_names': [step.name for step in self.executed_steps],
            'rollback_executed': self.is_rollback_executed(),
            'strategies': list(self.strategies.keys()) if self.strategies else [],
        }
