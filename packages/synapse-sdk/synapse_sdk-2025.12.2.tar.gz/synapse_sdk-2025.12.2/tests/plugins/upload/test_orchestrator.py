from unittest.mock import Mock

import pytest

from synapse_sdk.plugins.categories.upload.actions.upload.context import StepResult, UploadContext
from synapse_sdk.plugins.categories.upload.actions.upload.orchestrator import UploadOrchestrator
from synapse_sdk.plugins.categories.upload.actions.upload.registry import StepRegistry
from synapse_sdk.plugins.categories.upload.actions.upload.steps.base import BaseStep


class MockStep(BaseStep):
    """Mock step for testing."""

    def __init__(
        self,
        name: str,
        weight: float = 0.2,
        should_fail: bool = False,
        can_skip: bool = False,
        rollback_should_fail: bool = False,
    ):
        self._name = name
        self._weight = weight
        self.should_fail = should_fail
        self._can_skip = can_skip
        self.rollback_should_fail = rollback_should_fail
        self.executed = False
        self.rolled_back = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def progress_weight(self) -> float:
        return self._weight

    def execute(self, context: UploadContext) -> StepResult:
        self.executed = True
        if self.should_fail:
            return self.create_error_result(f'Step {self.name} failed')
        return self.create_success_result({'step_data': f'{self.name}_data'})

    def can_skip(self, context: UploadContext) -> bool:
        return self._can_skip

    def rollback(self, context: UploadContext) -> None:
        self.rolled_back = True
        if self.rollback_should_fail:
            raise Exception(f'Rollback failed for {self.name}')


class TestUploadOrchestrator:
    """Test UploadOrchestrator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_run = Mock()
        self.mock_client = Mock()
        self.params = {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}
        self.context = UploadContext(self.params, self.mock_run, self.mock_client)
        self.step_registry = StepRegistry()
        self.strategies = {
            'validation': Mock(),
            'file_discovery': Mock(),
            'metadata': Mock(),
            'upload': Mock(),
            'data_unit': Mock(),
        }

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = UploadOrchestrator(self.context, self.step_registry, self.strategies)

        assert orchestrator.context == self.context
        assert orchestrator.step_registry == self.step_registry
        assert orchestrator.strategies == self.strategies
        assert orchestrator.executed_steps == []
        assert orchestrator.current_step_index == 0

    def test_successful_workflow_execution(self):
        """Test successful execution of complete workflow."""
        # Register test steps
        step1 = MockStep('step1', 0.3)
        step2 = MockStep('step2', 0.4)
        step3 = MockStep('step3', 0.3)

        self.step_registry.register(step1)
        self.step_registry.register(step2)
        self.step_registry.register(step3)

        orchestrator = UploadOrchestrator(self.context, self.step_registry, self.strategies)

        # Execute workflow
        result = orchestrator.execute()

        # Verify all steps were executed
        assert step1.executed is True
        assert step2.executed is True
        assert step3.executed is True

        # Verify no rollbacks
        assert step1.rolled_back is False
        assert step2.rolled_back is False
        assert step3.rolled_back is False

        # Verify orchestrator state
        assert len(orchestrator.executed_steps) == 3
        assert orchestrator.current_step_index == 2

        # Verify result
        assert result['success'] is True
        assert len(result['errors']) == 0

    def test_workflow_with_step_failure(self):
        """Test workflow execution when a step fails."""
        # Register test steps - second step will fail
        step1 = MockStep('step1')
        step2 = MockStep('step2', should_fail=True)
        step3 = MockStep('step3')

        self.step_registry.register(step1)
        self.step_registry.register(step2)
        self.step_registry.register(step3)

        orchestrator = UploadOrchestrator(self.context, self.step_registry, self.strategies)

        # Execute workflow - should raise exception
        with pytest.raises(Exception, match="Step 'step2' failed"):
            orchestrator.execute()

        # Verify only first step was executed
        assert step1.executed is True
        assert step2.executed is True
        assert step3.executed is False

        # Verify rollback was called on executed steps
        assert step1.rolled_back is True
        assert step2.rolled_back is False  # Failed step not added to executed list
        assert step3.rolled_back is False

        # Verify orchestrator state
        assert len(orchestrator.executed_steps) == 1  # Only step1 was successful
        assert orchestrator.is_rollback_executed() is True

    def test_workflow_with_skipped_steps(self):
        """Test workflow execution with skippable steps."""
        step1 = MockStep('step1')
        step2 = MockStep('step2', can_skip=True)
        step3 = MockStep('step3')

        self.step_registry.register(step1)
        self.step_registry.register(step2)
        self.step_registry.register(step3)

        orchestrator = UploadOrchestrator(self.context, self.step_registry, self.strategies)

        orchestrator.execute()

        # Verify step execution
        assert step1.executed is True
        assert step2.executed is False  # Should be skipped
        assert step3.executed is True

        # Verify only non-skipped steps are in executed list
        assert len(orchestrator.executed_steps) == 2
        executed_names = [step.name for step in orchestrator.executed_steps]
        assert 'step1' in executed_names
        assert 'step2' not in executed_names
        assert 'step3' in executed_names

    def test_rollback_with_failure(self):
        """Test rollback behavior when rollback itself fails."""
        step1 = MockStep('step1', rollback_should_fail=True)
        step2 = MockStep('step2', should_fail=True)

        self.step_registry.register(step1)
        self.step_registry.register(step2)

        orchestrator = UploadOrchestrator(self.context, self.step_registry, self.strategies)

        # Execute workflow - should handle rollback failure gracefully
        with pytest.raises(Exception, match="Step 'step2' failed"):
            orchestrator.execute()

        # Verify rollback was attempted despite failure
        assert step1.rolled_back is True
        assert orchestrator.is_rollback_executed() is True

    def test_strategy_injection(self):
        """Test that strategies are injected into context."""
        step = MockStep('test_step')
        self.step_registry.register(step)

        orchestrator = UploadOrchestrator(self.context, self.step_registry, self.strategies)
        orchestrator.execute()

        # Verify strategies were injected
        assert hasattr(self.context, 'strategies')
        assert self.context.strategies == self.strategies

    def test_progress_tracking(self):
        """Test progress tracking during workflow execution."""
        step1 = MockStep('step1', 0.2)
        step2 = MockStep('step2', 0.3)
        step3 = MockStep('step3', 0.5)

        self.step_registry.register(step1)
        self.step_registry.register(step2)
        self.step_registry.register(step3)

        orchestrator = UploadOrchestrator(self.context, self.step_registry, self.strategies)
        orchestrator.execute()

        # Check final progress metrics
        workflow_metrics = self.context.metrics.get('workflow', {})
        assert workflow_metrics['total_steps'] == 3
        assert workflow_metrics['current_step'] == 3
        assert workflow_metrics['total_weight'] == 1.0
        assert workflow_metrics['completed_weight'] == 1.0
        assert workflow_metrics['progress_percentage'] == 100.0

    def test_workflow_summary(self):
        """Test getting workflow summary."""
        step1 = MockStep('step1')
        step2 = MockStep('step2')

        self.step_registry.register(step1)
        self.step_registry.register(step2)

        orchestrator = UploadOrchestrator(self.context, self.step_registry, self.strategies)
        orchestrator.execute()

        summary = orchestrator.get_workflow_summary()

        assert summary['total_steps'] == 2
        assert summary['executed_steps'] == 2
        assert summary['step_names'] == ['step1', 'step2']
        assert summary['executed_step_names'] == ['step1', 'step2']
        assert summary['rollback_executed'] is False
        assert len(summary['strategies']) == 5

    def test_empty_workflow(self):
        """Test execution with no registered steps."""
        orchestrator = UploadOrchestrator(self.context, self.step_registry, self.strategies)

        result = orchestrator.execute()

        assert result['success'] is True
        assert len(orchestrator.executed_steps) == 0

    def test_exception_during_execution(self):
        """Test handling of unexpected exceptions during step execution."""

        class ExceptionStep(BaseStep):
            @property
            def name(self) -> str:
                return 'exception_step'

            @property
            def progress_weight(self) -> float:
                return 1.0

            def execute(self, context: UploadContext) -> StepResult:
                raise ValueError('Unexpected error')

            def can_skip(self, context: UploadContext) -> bool:
                return False

            def rollback(self, context: UploadContext) -> None:
                pass

        exception_step = ExceptionStep()
        self.step_registry.register(exception_step)

        orchestrator = UploadOrchestrator(self.context, self.step_registry, self.strategies)

        with pytest.raises(ValueError, match='Unexpected error'):
            orchestrator.execute()

        assert orchestrator.is_rollback_executed() is True
