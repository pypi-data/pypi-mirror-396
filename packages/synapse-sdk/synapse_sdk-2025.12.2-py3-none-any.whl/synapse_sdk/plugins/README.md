# Synapse SDK Plugin System - Developer Reference

This document provides comprehensive guidance for developers working on the Synapse SDK plugin system architecture, internal APIs, and core infrastructure.

## Overview

The Synapse SDK plugin system is a modular framework that enables distributed execution of ML operations across different categories and execution methods. The system is built around the concept of **actions** - discrete operations that can be packaged, distributed, and executed in various environments.

### Architecture

```
synapse_sdk/plugins/
├── categories/           # Plugin category implementations
│   ├── base.py          # Action base class
│   ├── decorators.py    # Registration decorators
│   ├── registry.py      # Action registry
│   ├── neural_net/      # Neural network actions
│   ├── export/          # Data export actions
│   ├── upload/          # File upload actions
│   ├── smart_tool/      # AI-powered tools
│   ├── pre_annotation/  # Pre-processing actions
│   ├── post_annotation/ # Post-processing actions
│   └── data_validation/ # Validation actions
├── templates/           # Cookiecutter templates
├── utils/              # Utility functions
├── models.py           # Core plugin models
├── enums.py            # Plugin enums
└── exceptions.py       # Plugin exceptions
```

### Key Features

- **🔌 Modular Architecture**: Self-contained plugins with isolated dependencies
- **⚡ Multiple Execution Methods**: Jobs, Tasks, and REST API endpoints
- **📦 Distributed Execution**: Ray-based scalable computing
- **🛠️ Template System**: Cookiecutter-based scaffolding
- **📊 Progress Tracking**: Built-in logging, metrics, and progress monitoring
- **🔄 Dynamic Loading**: Runtime plugin discovery and registration

## Core Components

### Action Base Class

The `Action` class (`synapse_sdk/plugins/categories/base.py`) provides the unified interface for all plugin actions:

```python
class Action:
    """Base class for all plugin actions.

    Class Variables:
        name (str): Action identifier
        category (PluginCategory): Plugin category
        method (RunMethod): Execution method
        run_class (Run): Run management class
        params_model (BaseModel): Parameter validation model
        progress_categories (Dict): Progress tracking categories
        metrics_categories (Dict): Metrics collection categories

    Instance Variables:
        params (Dict): Validated action parameters
        plugin_config (Dict): Plugin configuration
        plugin_release (PluginRelease): Plugin metadata
        client: Backend API client
        run (Run): Execution instance
    """

    # Class configuration
    name = None
    category = None
    method = None
    run_class = Run
    params_model = None
    progress_categories = None
    metrics_categories = None

    def start(self):
        """Main action logic - implement in subclasses."""
        raise NotImplementedError
```

### Plugin Categories

The system supports seven main categories defined in `enums.py`:

```python
class PluginCategory(Enum):
    NEURAL_NET = 'neural_net'          # ML training and inference
    EXPORT = 'export'                  # Data export operations
    UPLOAD = 'upload'                  # File upload functionality
    SMART_TOOL = 'smart_tool'          # AI-powered automation
    POST_ANNOTATION = 'post_annotation' # Post-processing
    PRE_ANNOTATION = 'pre_annotation'   # Pre-processing
    DATA_VALIDATION = 'data_validation' # Quality checks
```

### Execution Methods

Three execution methods are supported:

```python
class RunMethod(Enum):
    JOB = 'job'        # Long-running distributed tasks
    TASK = 'task'      # Simple operations
    RESTAPI = 'restapi' # HTTP endpoints
```

### Run Management

The `Run` class (`models.py`) manages action execution:

```python
class Run(BaseModel):
    """Manages plugin execution lifecycle.

    Key Methods:
        log_message(message, context): Log execution messages
        set_progress(current, total, category): Update progress
        set_metrics(metrics, category): Record metrics
        log(log_type, data): Structured logging
    """

    def log_message(self, message: str, context: str = 'INFO'):
        """Log execution messages with context."""

    def set_progress(self, current: int, total: int, category: str = None):
        """Update progress tracking."""

    def set_metrics(self, metrics: dict, category: str):
        """Record execution metrics."""
```

## Creating Plugin Categories

### 1. Define Category Structure

Create a new category directory:

```
synapse_sdk/plugins/categories/my_category/
├── __init__.py
├── actions/
│   ├── __init__.py
│   └── my_action.py
└── templates/
    └── plugin/
        ├── __init__.py
        └── my_action.py
```

### 2. Implement Base Action

```python
# synapse_sdk/plugins/categories/my_category/actions/my_action.py
from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from pydantic import BaseModel

class MyActionParams(BaseModel):
    """Parameter model for validation."""
    input_path: str
    output_path: str
    config: dict = {}

@register_action
class MyAction(Action):
    """Base implementation for my_category actions."""

    name = 'my_action'
    category = PluginCategory.MY_CATEGORY
    method = RunMethod.JOB
    params_model = MyActionParams

    progress_categories = {
        'preprocessing': {'proportion': 20},
        'processing': {'proportion': 60},
        'postprocessing': {'proportion': 20}
    }

    metrics_categories = {
        'performance': {
            'throughput': 0,
            'latency': 0,
            'accuracy': 0
        }
    }

    def start(self):
        """Main execution logic."""
        self.run.log_message("Starting my action...")

        # Access validated parameters
        input_path = self.params['input_path']
        output_path = self.params['output_path']

        # Update progress
        self.run.set_progress(0, 100, 'preprocessing')

        # Your implementation here
        result = self.process_data(input_path, output_path)

        # Record metrics
        self.run.set_metrics({
            'throughput': result['throughput'],
            'items_processed': result['count']
        }, 'performance')

        self.run.log_message("Action completed successfully")
        return result

    def process_data(self, input_path, output_path):
        """Implement category-specific logic."""
        raise NotImplementedError("Subclasses must implement process_data")
```

### 3. Create Template

```python
# synapse_sdk/plugins/categories/my_category/templates/plugin/my_action.py
from synapse_sdk.plugins.categories.my_category import MyAction as BaseMyAction

class MyAction(BaseMyAction):
    """Custom implementation of my_action."""

    def process_data(self, input_path, output_path):
        """Custom data processing logic."""
        # Plugin developer implements this
        return {"status": "success", "items_processed": 100}
```

### 4. Register Category

Update `enums.py`:

```python
class PluginCategory(Enum):
    # ... existing categories
    MY_CATEGORY = 'my_category'
```

## Action Implementation Examples

### Upload Action Architecture

The upload action demonstrates modular action architecture:

```
# Structure after SYN-5306 refactoring
synapse_sdk/plugins/categories/upload/actions/upload/
├── __init__.py      # Public API exports
├── action.py        # Main UploadAction class
├── run.py          # UploadRun execution management
├── models.py       # UploadParams validation
├── enums.py        # LogCode and LOG_MESSAGES
├── exceptions.py   # Custom exceptions
└── utils.py        # Utility classes
```

**Key Implementation Details:**

```python
# upload/action.py
@register_action
class UploadAction(Action):
    name = 'upload'
    category = PluginCategory.UPLOAD
    method = RunMethod.JOB
    run_class = UploadRun

    def start(self):
        # Comprehensive upload workflow
        storage_id = self.params.get('storage')
        path = self.params.get('path')

        # Setup and validation
        storage = self.client.get_storage(storage_id)
        pathlib_cwd = get_pathlib(storage, path)

        # Excel metadata processing
        excel_metadata = self._read_excel_metadata(pathlib_cwd)

        # File organization and upload
        file_specification = self._analyze_collection()
        organized_files = self._organize_files(pathlib_cwd, file_specification, excel_metadata)

        # Upload files
        uploaded_files = self._upload_files(organized_files)

        # Data unit generation
        generated_data_units = self._generate_data_units(uploaded_files, batch_size)

        return {
            'uploaded_files_count': len(uploaded_files),
            'generated_data_units_count': len(generated_data_units)
        }
```

## Plugin Action Structure Guidelines

For complex actions that require multiple components, follow the modular structure pattern established by the refactored upload action. This approach improves maintainability, testability, and code organization.

## Complex Action Refactoring Patterns

### Overview

As plugin actions evolve and grow in complexity, they often become monolithic files with 900+ lines containing multiple responsibilities. The SYN-5398 UploadAction refactoring demonstrates how to break down complex actions using **Strategy** and **Facade** design patterns, transforming a 1,600+ line monolithic implementation into a maintainable, testable architecture.

### When to Apply Complex Refactoring

Consider refactoring when your action exhibits:

- **Size**: 900+ lines in a single method or file
- **Multiple Responsibilities**: Handling validation, file processing, uploads, metadata extraction in one method
- **Conditional Complexity**: Multiple if/else branches for different processing strategies
- **Testing Difficulty**: Hard to unit test individual components
- **Maintenance Issues**: Changes require touching multiple unrelated sections

### Strategy Pattern for Pluggable Behaviors

The Strategy pattern allows you to define a family of algorithms, encapsulate each one, and make them interchangeable. This is ideal for actions that need different implementations of the same behavior.

#### Core Strategy Types

Based on the UploadAction refactoring, identify these key strategy categories:

```python
# 1. ValidationStrategy - Parameter and environment validation
class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, context: ActionContext) -> ValidationResult:
        """Validate parameters and environment."""
        pass

class UploadValidationStrategy(ValidationStrategy):
    def validate(self, context: ActionContext) -> ValidationResult:
        # Validate storage, collection, file paths
        return ValidationResult(is_valid=True, errors=[])

# 2. FileDiscoveryStrategy - Different file discovery methods
class FileDiscoveryStrategy(ABC):
    @abstractmethod
    def discover_files(self, context: ActionContext) -> List[Path]:
        """Discover files to process."""
        pass

class RecursiveFileDiscoveryStrategy(FileDiscoveryStrategy):
    def discover_files(self, context: ActionContext) -> List[Path]:
        # Recursive directory traversal
        return list(context.base_path.rglob("*"))

# 3. MetadataStrategy - Various metadata extraction approaches
class MetadataStrategy(ABC):
    @abstractmethod
    def extract_metadata(self, files: List[Path], context: ActionContext) -> Dict:
        """Extract metadata from files."""
        pass

class ExcelMetadataStrategy(MetadataStrategy):
    def extract_metadata(self, files: List[Path], context: ActionContext) -> Dict:
        # Excel-specific metadata extraction
        return {"excel_sheets": [], "total_rows": 0}

# 4. UploadStrategy - Different upload implementations
class UploadStrategy(ABC):
    @abstractmethod
    def upload_files(self, files: List[Path], context: ActionContext) -> List[UploadResult]:
        """Upload files using specific strategy."""
        pass

class StandardUploadStrategy(UploadStrategy):
    def upload_files(self, files: List[Path], context: ActionContext) -> List[UploadResult]:
        # Standard upload implementation
        return [self._upload_single(f) for f in files]

# 5. DataUnitStrategy - Different data unit generation methods
class DataUnitStrategy(ABC):
    @abstractmethod
    def generate_data_units(self, uploaded_files: List[UploadResult], context: ActionContext) -> List[DataUnit]:
        """Generate data units from uploaded files."""
        pass

class StandardDataUnitStrategy(DataUnitStrategy):
    def generate_data_units(self, uploaded_files: List[UploadResult], context: ActionContext) -> List[DataUnit]:
        # Standard data unit creation
        return [DataUnit(file=file) for file in uploaded_files]
```

#### Strategy Factory Pattern

Use a factory to create appropriate strategies based on configuration:

```python
class StrategyFactory:
    """Factory for creating action strategies based on context."""

    @staticmethod
    def create_validation_strategy(context: ActionContext) -> ValidationStrategy:
        if context.params.get('strict_validation', False):
            return StrictValidationStrategy()
        return StandardValidationStrategy()

    @staticmethod
    def create_upload_strategy(context: ActionContext) -> UploadStrategy:
        return StandardUploadStrategy()

    @staticmethod
    def create_file_discovery_strategy(context: ActionContext) -> FileDiscoveryStrategy:
        if context.params.get('is_recursive', False):
            return RecursiveFileDiscoveryStrategy()
        return FlatFileDiscoveryStrategy()
```

### Facade Pattern with Orchestrator

The Facade pattern provides a simplified interface to a complex subsystem. The **Orchestrator** coordinates all strategies through a step-based workflow.

#### Orchestrator Implementation

```python
class UploadOrchestrator:
    """Facade that orchestrates the complete upload workflow."""

    def __init__(self, context: ActionContext):
        self.context = context
        self.factory = StrategyFactory()
        self.steps_completed = []

        # Initialize strategies
        self.validation_strategy = self.factory.create_validation_strategy(context)
        self.file_discovery_strategy = self.factory.create_file_discovery_strategy(context)
        self.metadata_strategy = self.factory.create_metadata_strategy(context)
        self.upload_strategy = self.factory.create_upload_strategy(context)
        self.data_unit_strategy = self.factory.create_data_unit_strategy(context)

    def execute_workflow(self) -> UploadResult:
        """Execute the complete upload workflow with rollback support."""
        try:
            # Step 1: Setup and validation
            self._execute_step("setup_validation", self._setup_and_validate)

            # Step 2: File discovery
            files = self._execute_step("file_discovery", self._discover_files)

            # Step 3: Excel metadata extraction
            metadata = self._execute_step("metadata_extraction",
                                              lambda: self._extract_metadata(files))

            # Step 4: File organization
            organized_files = self._execute_step("file_organization",
                                                     lambda: self._organize_files(files, metadata))

            # Step 5: File upload
            uploaded_files = self._execute_step("file_upload",
                                                    lambda: self._upload_files(organized_files))

            # Step 6: Data unit generation
            data_units = self._execute_step("data_unit_generation",
                                                lambda: self._generate_data_units(uploaded_files))

            # Step 7: Cleanup
            self._execute_step("cleanup", self._cleanup_temp_files)

            # Step 8: Result aggregation
            return self._execute_step("result_aggregation",
                                          lambda: self._aggregate_results(uploaded_files, data_units))

        except Exception as e:
            self._rollback_completed_steps()
            raise UploadOrchestrationError(f"Workflow failed at step {len(self.steps_completed)}: {e}")

    def _execute_step(self, step_name: str, step_func: callable):
        """Execute a workflow step with error handling and progress tracking."""
        self.context.logger.log_message_with_code(LogCode.STEP_STARTED, step_name)

        try:
            result = step_func()
            self.steps_completed.append(step_name)
            self.context.logger.log_message_with_code(LogCode.STEP_COMPLETED, step_name)
            return result
        except Exception as e:
            self.context.logger.log_message_with_code(LogCode.STEP_FAILED, step_name, str(e))
            raise

    def _setup_and_validate(self):
        """Step 1: Setup and validation using strategy."""
        validation_result = self.validation_strategy.validate(self.context)
        if not validation_result.is_valid:
            raise ValidationError(f"Validation failed: {validation_result.errors}")

    def _discover_files(self) -> List[Path]:
        """Step 2: File discovery using strategy."""
        return self.file_discovery_strategy.discover_files(self.context)

    def _extract_metadata(self, files: List[Path]) -> Dict:
        """Step 3: Metadata extraction using strategy."""
        return self.metadata_strategy.extract_metadata(files, self.context)

    def _upload_files(self, files: List[Path]) -> List[UploadResult]:
        """Step 5: File upload using strategy."""
        return self.upload_strategy.upload_files(files, self.context)

    def _generate_data_units(self, uploaded_files: List[UploadResult]) -> List[DataUnit]:
        """Step 6: Data unit generation using strategy."""
        return self.data_unit_strategy.generate_data_units(uploaded_files, self.context)

    def _rollback_completed_steps(self):
        """Rollback completed steps in reverse order."""
        for step in reversed(self.steps_completed):
            try:
                rollback_method = getattr(self, f"_rollback_{step}", None)
                if rollback_method:
                    rollback_method()
            except Exception as e:
                self.context.logger.log_message_with_code(LogCode.ROLLBACK_FAILED, step, str(e))
```

#### Transformed Action Implementation

The main action becomes dramatically simplified:

```python
# Before: 900+ line monolithic start() method
class UploadAction(Action):
    def start(self):
        # 900+ lines of mixed responsibilities...

# After: Clean, orchestrated implementation (196 lines total)
class UploadAction(Action):
    """Upload action using Strategy and Facade patterns."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = ActionContext(
            params=self.params,
            client=self.client,
            logger=self.run,
            workspace=self.get_workspace_path()
        )

    def start(self) -> UploadResult:
        """Main action execution using orchestrator facade."""
        self.run.log_message_with_code(LogCode.UPLOAD_STARTED)

        try:
            # Create and execute orchestrator
            orchestrator = UploadOrchestrator(self.context)
            result = orchestrator.execute_workflow()

            self.run.log_message_with_code(LogCode.UPLOAD_COMPLETED,
                                         result.uploaded_files_count, result.data_units_count)
            return result

        except Exception as e:
            self.run.log_message_with_code(LogCode.UPLOAD_FAILED, str(e))
            raise ActionError(f"Upload action failed: {e}")
```

### Context Management

Use a shared context object to pass state between strategies and orchestrator:

```python
@dataclass
class ActionContext:
    """Shared context for action execution."""
    params: Dict[str, Any]
    client: Any
    logger: Any
    workspace: Path
    temp_files: List[Path] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def add_temp_file(self, file_path: Path):
        """Track temporary files for cleanup."""
        self.temp_files.append(file_path)

    def update_metrics(self, category: str, metrics: Dict[str, Any]):
        """Update execution metrics."""
        if category not in self.metrics:
            self.metrics[category] = {}
        self.metrics[category].update(metrics)
```

### Migration Guide for Complex Actions

#### Step 1: Identify Strategy Boundaries

Analyze your monolithic action to identify:

1. **Different algorithms** for the same operation (validation methods, file processing approaches)
2. **Configurable behaviors** that change based on parameters
3. **Testable units** that can be isolated

#### Step 2: Extract Strategies

```python
# Before: Mixed responsibilities in one method
def start(self):
    # validation logic (100 lines)
    if self.params.get('strict_mode'):
        # strict validation
    else:
        # standard validation

    # file discovery logic (150 lines)
    if self.params.get('recursive'):
        # recursive discovery
    else:
        # flat discovery

    # upload logic (200 lines)
    # Direct upload implementation
    uploaded_files = self._upload_files(organized_files)

# After: Separated into strategies
class StrictValidationStrategy(ValidationStrategy): ...
class StandardValidationStrategy(ValidationStrategy): ...
class RecursiveFileDiscoveryStrategy(FileDiscoveryStrategy): ...
class StandardUploadStrategy(UploadStrategy): ...
```

#### Step 3: Create Orchestrator

Design your workflow steps:

1. Define clear step boundaries
2. Implement rollback for each step
3. Add progress tracking and logging
4. Handle errors gracefully

#### Step 4: Update Action Class

Transform the main action to use the orchestrator:

1. Create context object
2. Initialize orchestrator
3. Execute workflow
4. Handle results and errors

### Benefits and Metrics

The SYN-5398 refactoring achieved:

#### **Code Reduction**

- Main action: 900+ lines → 196 lines (-78% reduction)
- Total codebase: 1,600+ lines → 1,400+ lines (better organized)
- Cyclomatic complexity: High → Low (single responsibility per class)

#### **Improved Testability**

- **89 passing tests** with individual strategy testing
- **Isolated unit tests** for each strategy component
- **Integration tests** for orchestrator workflow
- **Rollback testing** for error scenarios

#### **Better Maintainability**

- **Single responsibility** per strategy class
- **Clear separation** of concerns
- **Reusable strategies** across different actions
- **Easy to extend** with new strategy implementations

#### **Enhanced Flexibility**

- **Runtime strategy selection** based on parameters
- **Pluggable algorithms** without changing core logic
- **Configuration-driven** behavior changes
- **A/B testing support** through strategy switching

### Example: Converting a Complex Action

```python
# Before: Monolithic action (simplified example)
class ComplexAction(Action):
    def start(self):
        # 50 lines of validation
        if self.params.get('validation_type') == 'strict':
            # strict validation logic
        else:
            # standard validation logic

        # 100 lines of data processing
        if self.params.get('processing_method') == 'batch':
            # batch processing logic
        else:
            # stream processing logic

        # 80 lines of output generation
        if self.params.get('output_format') == 'json':
            # JSON output logic
        else:
            # CSV output logic

# After: Strategy-based action
class ComplexAction(Action):
    def start(self):
        context = ActionContext(params=self.params, logger=self.run)
        orchestrator = ComplexActionOrchestrator(context)
        return orchestrator.execute_workflow()

# Individual strategies (testable, reusable)
class StrictValidationStrategy(ValidationStrategy): ...
class BatchProcessingStrategy(ProcessingStrategy): ...
class JSONOutputStrategy(OutputStrategy): ...
```

This pattern transformation makes complex actions maintainable, testable, and extensible while preserving all original functionality.

### Recommended File Structure

```
synapse_sdk/plugins/categories/{category}/actions/{action}/
├── __init__.py          # Public API exports
├── action.py            # Main action implementation
├── run.py               # Execution and logging management
├── models.py            # Pydantic parameter models
├── enums.py             # Enums and message constants
├── exceptions.py        # Custom exception classes
├── utils.py             # Helper utilities and configurations
└── README.md            # Action-specific documentation
```

### Module Responsibilities

#### 1. `__init__.py` - Public API

Defines the public interface and maintains backward compatibility:

```python
# Export all public classes for backward compatibility
from .action import UploadAction
from .enums import LogCode, LOG_MESSAGES, UploadStatus
from .exceptions import ExcelParsingError, ExcelSecurityError
from .models import UploadParams
from .run import UploadRun
from .utils import ExcelSecurityConfig, PathAwareJSONEncoder

__all__ = [
    'UploadAction',
    'UploadRun',
    'UploadParams',
    'UploadStatus',
    'LogCode',
    'LOG_MESSAGES',
    'ExcelSecurityError',
    'ExcelParsingError',
    'PathAwareJSONEncoder',
    'ExcelSecurityConfig',
]
```

#### 2. `action.py` - Main Implementation

Contains the core action logic, inheriting from the base `Action` class:

```python
from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod

from .enums import LogCode
from .models import UploadParams
from .run import UploadRun

class UploadAction(Action):
    """Main upload action implementation."""

    name = 'upload'
    category = PluginCategory.UPLOAD
    method = RunMethod.JOB
    run_class = UploadRun
    params_model = UploadParams

    def start(self):
        """Main action logic."""
        # Validate parameters
        self.validate_params()

        # Log start
        self.run.log_message_with_code(LogCode.UPLOAD_STARTED)

        # Execute main logic
        result = self._process_upload()

        # Log completion
        self.run.log_message_with_code(LogCode.UPLOAD_COMPLETED)

        return result
```

#### 3. `models.py` - Parameter Validation

Defines Pydantic models for type-safe parameter validation:

```python
from typing import Annotated
from pydantic import AfterValidator, BaseModel, field_validator
from synapse_sdk.utils.pydantic.validators import non_blank

class UploadParams(BaseModel):
    """Upload action parameters with validation."""

    name: Annotated[str, AfterValidator(non_blank)]
    description: str | None = None
    path: str
    storage: int
    collection: int
    project: int | None = None
    is_recursive: bool = False
    max_file_size_mb: int = 50

    @field_validator('storage', mode='before')
    @classmethod
    def check_storage_exists(cls, value: str, info) -> str:
        """Validate storage exists via API."""
        action = info.context['action']
        client = action.client
        try:
            client.get_storage(value)
        except ClientError:
            raise PydanticCustomError('client_error', 'Storage not found')
        return value
```

#### 4. `enums.py` - Constants and Enums

Centralizes all enum definitions and constant values:

```python
from enum import Enum
from synapse_sdk.plugins.enums import Context

class UploadStatus(str, Enum):
    """Upload processing status."""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

class LogCode(str, Enum):
    """Type-safe logging codes."""
    UPLOAD_STARTED = 'UPLOAD_STARTED'
    VALIDATION_FAILED = 'VALIDATION_FAILED'
    NO_FILES_FOUND = 'NO_FILES_FOUND'
    UPLOAD_COMPLETED = 'UPLOAD_COMPLETED'
    # ... additional codes

LOG_MESSAGES = {
    LogCode.UPLOAD_STARTED: {
        'message': 'Upload process started.',
        'level': Context.INFO,
    },
    LogCode.VALIDATION_FAILED: {
        'message': 'Validation failed: {}',
        'level': Context.DANGER,
    },
    # ... message configurations
}
```

#### 5. `run.py` - Execution Management

Handles execution flow, progress tracking, and specialized logging:

```python
from typing import Optional
from synapse_sdk.plugins.models import Run
from synapse_sdk.plugins.enums import Context

from .enums import LogCode, LOG_MESSAGES

class UploadRun(Run):
    """Specialized run management for upload actions."""

    def log_message_with_code(self, code: LogCode, *args, level: Optional[Context] = None):
        """Type-safe logging with predefined messages."""
        if code not in LOG_MESSAGES:
            self.log_message(f'Unknown log code: {code}')
            return

        log_config = LOG_MESSAGES[code]
        message = log_config['message'].format(*args) if args else log_config['message']
        log_level = level or log_config['level']

        self.log_message(message, context=log_level.value)

    def log_upload_event(self, code: LogCode, *args, level: Optional[Context] = None):
        """Log upload-specific events with metrics."""
        self.log_message_with_code(code, *args, level)
        # Additional upload-specific logging logic
```

#### 6. `exceptions.py` - Custom Exceptions

Defines action-specific exception classes:

```python
class ExcelSecurityError(Exception):
    """Raised when Excel file security validation fails."""
    pass

class ExcelParsingError(Exception):
    """Raised when Excel file parsing encounters errors."""
    pass

class UploadValidationError(Exception):
    """Raised when upload parameter validation fails."""
    pass
```

#### 7. `utils.py` - Helper Utilities

Contains utility classes and helper functions:

```python
import json
import os
from pathlib import Path

class PathAwareJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles Path objects."""

    def default(self, obj):
        if hasattr(obj, '__fspath__') or hasattr(obj, 'as_posix'):
            return str(obj)
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super().default(obj)

class ExcelSecurityConfig:
    """Configuration for Excel file security limits."""

    def __init__(self):
        self.MAX_FILE_SIZE_MB = int(os.getenv('EXCEL_MAX_FILE_SIZE_MB', '10'))
        self.MAX_ROWS = int(os.getenv('EXCEL_MAX_ROWS', '10000'))
        self.MAX_COLUMNS = int(os.getenv('EXCEL_MAX_COLUMNS', '50'))
```

### Migration Guide

#### From Monolithic to Modular Structure

1. **Identify Components**: Break down the monolithic action into logical components
2. **Extract Models**: Move parameter validation to `models.py`
3. **Separate Enums**: Move constants and enums to `enums.py`
4. **Create Utilities**: Extract helper functions to `utils.py`
5. **Update Imports**: Ensure backward compatibility through `__init__.py`

#### Example Migration Steps

```python
# Before: Single upload.py file (1362 lines)
class UploadAction(Action):
    # All code in one file...

# After: Modular structure
# action.py - Main logic (546 lines)
# models.py - Parameter validation (98 lines)
# enums.py - Constants and logging codes (156 lines)
# run.py - Execution management (134 lines)
# utils.py - Helper utilities (89 lines)
# exceptions.py - Custom exceptions (6 lines)
# __init__.py - Public API (20 lines)
```

### Benefits of Modular Structure

- **Maintainability**: Each file has a single responsibility
- **Testability**: Individual components can be tested in isolation
- **Reusability**: Utilities and models can be shared across actions
- **Type Safety**: Enum-based logging and strong parameter validation
- **Backward Compatibility**: Public API remains unchanged

**Logging System with Enums:**

```python
# upload/enums.py
class LogCode(str, Enum):
    VALIDATION_FAILED = 'VALIDATION_FAILED'
    NO_FILES_FOUND = 'NO_FILES_FOUND'
    # ... 36 total log codes

LOG_MESSAGES = {
    LogCode.VALIDATION_FAILED: {
        'message': 'Validation failed.',
        'level': Context.DANGER,
    },
    # ... message configurations
}

# upload/run.py
class UploadRun(Run):
    def log_message_with_code(self, code: LogCode, *args, level: Optional[Context] = None):
        """Type-safe logging with predefined messages."""
        if code not in LOG_MESSAGES:
            self.log_message(f'Unknown log code: {code}')
            return

        log_config = LOG_MESSAGES[code]
        message = log_config['message'].format(*args) if args else log_config['message']
        log_level = level or log_config['level'] or Context.INFO

        if log_level == Context.INFO.value:
            self.log_message(message, context=log_level.value)
        else:
            self.log_upload_event(code, *args, level)
```

## Development Workflow

### 1. Local Development Setup

```bash
# Set up development environment
cd synapse_sdk/plugins/categories/my_category
python -m pip install -e .

# Create test plugin
synapse plugin create --category my_category --debug
```

### 2. Action Testing

```python
# Test action implementation
from synapse_sdk.plugins.utils import get_action_class

# Get action class
ActionClass = get_action_class("my_category", "my_action")

# Create test instance
action = ActionClass(
    params={"input_path": "/test/data", "output_path": "/test/output"},
    plugin_config={"debug": True},
    envs={"TEST_MODE": "true"}
)

# Run action
result = action.run_action()
assert result["status"] == "success"
```

### 3. Integration Testing

```python
# Test with Ray backend
import ray
from synapse_sdk.clients.ray import RayClient

# Initialize Ray
ray.init()
client = RayClient()

# Test distributed execution
job_result = client.submit_job(
    entrypoint="python action.py",
    runtime_env=action.get_runtime_env()
)
```

## Advanced Features

### Custom Progress Categories

```python
class MyAction(Action):
    progress_categories = {
        'data_loading': {
            'proportion': 10,
            'description': 'Loading input data'
        },
        'feature_extraction': {
            'proportion': 30,
            'description': 'Extracting features'
        },
        'model_training': {
            'proportion': 50,
            'description': 'Training model'
        },
        'evaluation': {
            'proportion': 10,
            'description': 'Evaluating results'
        }
    }

    def start(self):
        # Update specific progress categories
        self.run.set_progress(50, 100, 'data_loading')
        self.run.set_progress(25, 100, 'feature_extraction')
```

### Runtime Environment Customization

```python
def get_runtime_env(self):
    """Customize execution environment."""
    env = super().get_runtime_env()

    # Add custom packages
    env['pip']['packages'].extend([
        'custom-ml-library==2.0.0',
        'specialized-tool>=1.5.0'
    ])

    # Set environment variables
    env['env_vars'].update({
        'CUDA_VISIBLE_DEVICES': '0,1',
        'OMP_NUM_THREADS': '8',
        'CUSTOM_CONFIG_PATH': '/app/config'
    })

    # Add working directory files
    env['working_dir_files'] = {
        'config.yaml': 'path/to/local/config.yaml',
        'model_weights.pth': 'path/to/weights.pth'
    }

    return env
```

### Parameter Validation Patterns

```python
from pydantic import BaseModel, validator, Field
from typing import Literal, Optional, List

class AdvancedParams(BaseModel):
    """Advanced parameter validation."""

    # Enum-like validation
    model_type: Literal["cnn", "transformer", "resnet"]

    # Range validation
    learning_rate: float = Field(gt=0, le=1, default=0.001)
    batch_size: int = Field(ge=1, le=1024, default=32)

    # File path validation
    data_path: str
    output_path: Optional[str] = None

    # Complex validation
    layers: List[int] = Field(min_items=1, max_items=10)

    @validator('data_path')
    def validate_data_path(cls, v):
        if not os.path.exists(v):
            raise ValueError(f'Data path does not exist: {v}')
        return v

    @validator('output_path')
    def validate_output_path(cls, v, values):
        if v is None:
            # Auto-generate from data_path
            data_path = values.get('data_path', '')
            return f"{data_path}_output"
        return v

    @validator('layers')
    def validate_layers(cls, v):
        if len(v) < 2:
            raise ValueError('Must specify at least 2 layers')
        if v[0] <= 0 or v[-1] <= 0:
            raise ValueError('Input and output layers must be positive')
        return v
```

## Best Practices

### 1. Action Design

- **Single Responsibility**: Each action should have one clear purpose
- **Parameterization**: Make actions configurable through well-defined parameters
- **Error Handling**: Implement comprehensive error handling and validation
- **Progress Reporting**: Provide meaningful progress updates for long operations

### 2. Code Organization

```python
# Good: Modular structure
class UploadAction(Action):
    def start(self):
        self._validate_inputs()
        files = self._discover_files()
        processed_files = self._process_files(files)
        return self._generate_output(processed_files)

    def _validate_inputs(self):
        """Separate validation logic."""
        pass

    def _discover_files(self):
        """Separate file discovery logic."""
        pass

# Good: Use of enums for constants
class LogCode(str, Enum):
    VALIDATION_FAILED = 'VALIDATION_FAILED'
    FILE_NOT_FOUND = 'FILE_NOT_FOUND'

# Good: Type hints and documentation
def process_batch(self, items: List[Dict[str, Any]], batch_size: int = 100) -> List[Dict[str, Any]]:
    """Process items in batches for memory efficiency.

    Args:
        items: List of items to process
        batch_size: Number of items per batch

    Returns:
        List of processed items
    """
```

### 3. Performance Optimization

```python
# Use simple sequential processing for file uploads
def _upload_files(self, files: List[Path]) -> List[UploadResult]:
    results = []
    for file_path in files:
        result = self._upload_file(file_path)
        results.append(result)
    return results

# Use generators for memory efficiency
def _process_large_dataset(self, data_source):
    """Process data in chunks to avoid memory issues."""
    for chunk in self._chunk_data(data_source, chunk_size=1000):
        processed_chunk = self._process_chunk(chunk)
        yield processed_chunk

        # Update progress
        self.run.set_progress(self.processed_count, self.total_count, 'processing')
```

### 4. Error Handling

```python
from synapse_sdk.plugins.exceptions import ActionError

class MyAction(Action):
    def start(self):
        try:
            return self._execute_main_logic()
        except ValidationError as e:
            self.run.log_message(f"Validation error: {e}", "ERROR")
            raise ActionError(f"Parameter validation failed: {e}")
        except FileNotFoundError as e:
            self.run.log_message(f"File not found: {e}", "ERROR")
            raise ActionError(f"Required file missing: {e}")
        except Exception as e:
            self.run.log_message(f"Unexpected error: {e}", "ERROR")
            raise ActionError(f"Action execution failed: {e}")
```

### 5. Security Considerations

```python
# Good: Validate file paths
def _validate_file_path(self, file_path: str) -> Path:
    """Validate and sanitize file paths."""
    path = Path(file_path).resolve()

    # Prevent directory traversal
    if not str(path).startswith(str(self.workspace_root)):
        raise ActionError(f"File path outside workspace: {path}")

    return path

# Good: Sanitize user inputs
def _sanitize_filename(self, filename: str) -> str:
    """Remove unsafe characters from filename."""
    import re
    # Remove path separators and control characters
    safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
    return safe_name[:255]  # Limit length

# Good: Validate data sizes
def _validate_data_size(self, data: bytes) -> None:
    """Check data size limits."""
    max_size = 100 * 1024 * 1024  # 100MB
    if len(data) > max_size:
        raise ActionError(f"Data too large: {len(data)} bytes (max: {max_size})")
```

## API Reference

### Core Classes

#### Action

Base class for all plugin actions.

**Methods:**

- `start()`: Main execution method (abstract)
- `run_action()`: Execute action with error handling
- `get_runtime_env()`: Get execution environment configuration
- `validate_params()`: Validate action parameters

#### Run

Manages action execution lifecycle.

**Methods:**

- `log_message(message, context)`: Log execution messages
- `set_progress(current, total, category)`: Update progress
- `set_metrics(metrics, category)`: Record metrics
- `log(log_type, data)`: Structured logging

#### PluginRelease

Manages plugin metadata and configuration.

**Attributes:**

- `code`: Plugin identifier
- `name`: Human-readable name
- `version`: Semantic version
- `category`: Plugin category
- `config`: Plugin configuration

### Utility Functions

```python
# synapse_sdk/plugins/utils/
from synapse_sdk.plugins.utils import (
    get_action_class,      # Get action class by category/name
    load_plugin_config,    # Load plugin configuration
    validate_plugin,       # Validate plugin structure
    register_plugin,       # Register plugin in system
)

# Usage examples
ActionClass = get_action_class("upload", "upload")
config = load_plugin_config("/path/to/plugin")
is_valid = validate_plugin("/path/to/plugin")
```

This README provides the foundation for developing and extending the Synapse SDK plugin system. For specific implementation examples, refer to the existing plugin categories and their respective documentation.
