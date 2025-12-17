from typing import Dict, List, Optional

from .steps.base import BaseStep


class StepRegistry:
    """Registry for managing workflow steps."""

    def __init__(self):
        self._steps: List[BaseStep] = []
        self._step_by_name: Dict[str, BaseStep] = {}

    def register(self, step: BaseStep) -> None:
        """Register a step in the workflow."""
        if step.name in self._step_by_name:
            raise ValueError(f"Step with name '{step.name}' already registered")

        self._steps.append(step)
        self._step_by_name[step.name] = step

    def unregister(self, step_name: str) -> bool:
        """Unregister a step by name. Returns True if step was found and removed."""
        if step_name not in self._step_by_name:
            return False

        step = self._step_by_name[step_name]
        self._steps.remove(step)
        del self._step_by_name[step_name]
        return True

    def get_steps(self) -> List[BaseStep]:
        """Get all registered steps in order."""
        return self._steps.copy()

    def get_step(self, name: str) -> Optional[BaseStep]:
        """Get a step by name."""
        return self._step_by_name.get(name)

    def has_step(self, name: str) -> bool:
        """Check if a step is registered."""
        return name in self._step_by_name

    def clear(self) -> None:
        """Clear all registered steps."""
        self._steps.clear()
        self._step_by_name.clear()

    def get_step_names(self) -> List[str]:
        """Get list of all registered step names."""
        return list(self._step_by_name.keys())

    def get_total_progress_weight(self) -> float:
        """Get total progress weight of all steps."""
        return sum(step.progress_weight for step in self._steps)

    def insert_step_after(self, after_step_name: str, new_step: BaseStep) -> None:
        """Insert a step after an existing step."""
        if after_step_name not in self._step_by_name:
            raise ValueError(f"Step '{after_step_name}' not found")

        if new_step.name in self._step_by_name:
            raise ValueError(f"Step with name '{new_step.name}' already registered")

        # Find the index of the step to insert after
        after_step = self._step_by_name[after_step_name]
        index = self._steps.index(after_step) + 1

        # Insert the new step
        self._steps.insert(index, new_step)
        self._step_by_name[new_step.name] = new_step

    def insert_step_before(self, before_step_name: str, new_step: BaseStep) -> None:
        """Insert a step before an existing step."""
        if before_step_name not in self._step_by_name:
            raise ValueError(f"Step '{before_step_name}' not found")

        if new_step.name in self._step_by_name:
            raise ValueError(f"Step with name '{new_step.name}' already registered")

        # Find the index of the step to insert before
        before_step = self._step_by_name[before_step_name]
        index = self._steps.index(before_step)

        # Insert the new step
        self._steps.insert(index, new_step)
        self._step_by_name[new_step.name] = new_step

    def reorder_steps(self, step_names: List[str]) -> None:
        """Reorder steps according to the provided list of step names."""
        if set(step_names) != set(self._step_by_name.keys()):
            raise ValueError('Step names list must contain all registered steps')

        # Reorder the steps list
        self._steps = [self._step_by_name[name] for name in step_names]

    def __len__(self) -> int:
        """Return number of registered steps."""
        return len(self._steps)

    def __iter__(self):
        """Iterate over registered steps."""
        return iter(self._steps)

    def __contains__(self, step_name: str) -> bool:
        """Check if step name is registered."""
        return step_name in self._step_by_name

    def __str__(self) -> str:
        step_names = [step.name for step in self._steps]
        return f'StepRegistry({step_names})'

    def __repr__(self) -> str:
        return f'StepRegistry(steps={len(self._steps)})'
