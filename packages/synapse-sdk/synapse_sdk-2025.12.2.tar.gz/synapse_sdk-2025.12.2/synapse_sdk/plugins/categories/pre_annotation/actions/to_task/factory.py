"""Factory for creating ToTask strategies based on context."""

from typing import Dict, Type

from .enums import AnnotationMethod
from .strategies.base import (
    AnnotationStrategy,
    DataExtractionStrategy,
    MetricsStrategy,
    PreProcessorStrategy,
    ValidationStrategy,
)


class ToTaskStrategyFactory:
    """Factory for creating action strategies based on context."""

    def __init__(self):
        # Import strategies here to avoid circular imports
        from .strategies.annotation import FileAnnotationStrategy, InferenceAnnotationStrategy
        from .strategies.extraction import FileUrlExtractionStrategy, InferenceDataExtractionStrategy
        from .strategies.metrics import ProgressTrackingStrategy
        from .strategies.preprocessor import PreProcessorManagementStrategy
        from .strategies.validation import (
            ProjectValidationStrategy,
            TargetSpecificationValidationStrategy,
            TaskValidationStrategy,
        )

        self._annotation_strategies: Dict[AnnotationMethod, Type[AnnotationStrategy]] = {
            AnnotationMethod.FILE: FileAnnotationStrategy,
            AnnotationMethod.INFERENCE: InferenceAnnotationStrategy,
        }

        self._validation_strategies = {
            'project': ProjectValidationStrategy,
            'task': TaskValidationStrategy,
            'target_spec': TargetSpecificationValidationStrategy,
        }

        self._extraction_strategies = {
            AnnotationMethod.FILE: FileUrlExtractionStrategy,
            AnnotationMethod.INFERENCE: InferenceDataExtractionStrategy,
        }

        self._preprocessor_strategy = PreProcessorManagementStrategy
        self._metrics_strategy = ProgressTrackingStrategy

    def create_annotation_strategy(self, method: AnnotationMethod) -> AnnotationStrategy:
        """Create annotation strategy based on method."""
        strategy_class = self._annotation_strategies.get(method)
        if not strategy_class:
            raise ValueError(f'No annotation strategy available for method: {method}')
        return strategy_class()

    def create_validation_strategy(self, validation_type: str) -> ValidationStrategy:
        """Create validation strategy based on type."""
        strategy_class = self._validation_strategies.get(validation_type)
        if not strategy_class:
            raise ValueError(f'No validation strategy available for type: {validation_type}')
        return strategy_class()

    def create_extraction_strategy(self, method: AnnotationMethod) -> DataExtractionStrategy:
        """Create data extraction strategy based on method."""
        strategy_class = self._extraction_strategies.get(method)
        if not strategy_class:
            raise ValueError(f'No extraction strategy available for method: {method}')
        return strategy_class()

    def create_preprocessor_strategy(self) -> PreProcessorStrategy:
        """Create pre-processor management strategy."""
        return self._preprocessor_strategy()

    def create_metrics_strategy(self) -> MetricsStrategy:
        """Create metrics tracking strategy."""
        return self._metrics_strategy()
