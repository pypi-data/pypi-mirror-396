from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .run import UploadRun


class StepResult:
    """Result of a workflow step execution."""

    def __init__(
        self,
        success: bool = True,
        data: Dict[str, Any] = None,
        error: str = None,
        rollback_data: Dict[str, Any] = None,
        skipped: bool = False,
        original_exception: Optional[Exception] = None,
    ):
        self.success = success
        self.data = data or {}
        self.error = error
        self.rollback_data = rollback_data or {}
        self.skipped = skipped
        self.original_exception = original_exception
        self.timestamp = datetime.now()

    def __bool__(self):
        return self.success


class UploadContext:
    """Shared context for all upload workflow steps."""

    def __init__(self, params: Dict, run: UploadRun, client: Any, action: Any = None):
        self.params = params
        self.run = run
        self.client = client
        self._action = action  # Reference to parent action for uploader access

        # Core state
        self.storage = None
        self.pathlib_cwd = None
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.file_specifications: Dict[str, Any] = {}
        self.organized_files: List[Dict[str, Any]] = []
        self.uploaded_files: List[Dict[str, Any]] = []
        self.data_units: List[Dict[str, Any]] = []

        # Progress and metrics
        self.metrics: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.step_results: List[StepResult] = []

        # Strategies (injected by orchestrator)
        self.strategies: Dict[str, Any] = {}

        # Rollback information
        self.rollback_data: Dict[str, Any] = {}

    def update(self, result: StepResult) -> None:
        """Update context with step results."""
        self.step_results.append(result)

        if result.success:
            # Update context state with step data
            for key, value in result.data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    # Store in a general data dictionary
                    if not hasattr(self, 'step_data'):
                        self.step_data = {}
                    self.step_data[key] = value

            # Store rollback data
            if result.rollback_data:
                self.rollback_data.update(result.rollback_data)
        else:
            # Record error
            if result.error:
                self.errors.append(result.error)

    def get_result(self) -> Dict[str, Any]:
        """Get final result dictionary."""
        return {
            'uploaded_files_count': len(self.uploaded_files),
            'generated_data_units_count': len(self.data_units),
            'success': len(self.errors) == 0,
            'errors': self.errors,
        }

    def has_errors(self) -> bool:
        """Check if context has any errors."""
        return len(self.errors) > 0

    def get_last_step_result(self) -> Optional[StepResult]:
        """Get the result of the last executed step."""
        return self.step_results[-1] if self.step_results else None

    def get_step_result_by_name(self, step_name: str) -> Optional[StepResult]:
        """Get step result by step name (stored in rollback_data)."""
        for result in self.step_results:
            if result.rollback_data.get('step_name') == step_name:
                return result
        return None

    def clear_errors(self) -> None:
        """Clear all errors (useful for retry scenarios)."""
        self.errors.clear()

    def add_error(self, error: str) -> None:
        """Add an error to the context."""
        self.errors.append(error)

    def get_param(self, key: str, default: Any = None) -> Any:
        """Get parameter value with default."""
        return self.params.get(key, default)

    def set_storage(self, storage: Any) -> None:
        """Set storage object."""
        self.storage = storage

    def set_pathlib_cwd(self, path: Path) -> None:
        """Set current working directory path."""
        self.pathlib_cwd = path

    def set_file_specifications(self, specs: Dict[str, Any]) -> None:
        """Set file specifications."""
        self.file_specifications = specs

    def add_organized_files(self, files: List[Dict[str, Any]]) -> None:
        """Add organized files to context."""
        self.organized_files.extend(files)

    def add_uploaded_files(self, files: List[Dict[str, Any]]) -> None:
        """Add uploaded files to context."""
        self.uploaded_files.extend(files)

    def add_data_units(self, units: List[Dict[str, Any]]) -> None:
        """Add data units to context."""
        self.data_units.extend(units)

    def update_metrics(self, category: str, metrics: Dict[str, Any]) -> None:
        """Update metrics for a specific category."""
        if category not in self.metrics:
            self.metrics[category] = {}
        self.metrics[category].update(metrics)

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context by key."""
        # First check direct attributes
        if hasattr(self, key):
            return getattr(self, key)

        # Then check step_data if it exists
        if hasattr(self, 'step_data') and key in self.step_data:
            return self.step_data[key]

        # Special mappings for expected keys
        if key == 'file_specification_template':
            return self.file_specifications
        elif key == 'pathlib_cwd':
            return self.pathlib_cwd
        elif key == 'organized_files':
            return self.organized_files

        return default

    def set(self, key: str, value: Any) -> None:
        """Set value in context by key."""
        # Special mappings for expected keys
        if key == 'file_specification_template':
            self.file_specifications = value
        elif key == 'pathlib_cwd':
            self.pathlib_cwd = value
        elif key == 'organized_files':
            self.organized_files = value
        elif hasattr(self, key):
            setattr(self, key, value)
        else:
            # Store in step_data
            if not hasattr(self, 'step_data'):
                self.step_data = {}
            self.step_data[key] = value
