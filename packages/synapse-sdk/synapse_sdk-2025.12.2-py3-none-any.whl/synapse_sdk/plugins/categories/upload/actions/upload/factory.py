from typing import Any, Dict

from .strategies.base import (
    DataUnitStrategy,
    FileDiscoveryStrategy,
    MetadataStrategy,
    UploadStrategy,
    ValidationStrategy,
)


class StrategyFactory:
    """Factory for creating strategy instances based on configuration."""

    def __init__(self):
        self._validation_strategies = {}
        self._file_discovery_strategies = {}
        self._metadata_strategies = {}
        self._upload_strategies = {}
        self._data_unit_strategies = {}

    def register_validation_strategy(self, name: str, strategy_class: type) -> None:
        """Register a validation strategy class."""
        self._validation_strategies[name] = strategy_class

    def register_file_discovery_strategy(self, name: str, strategy_class: type) -> None:
        """Register a file discovery strategy class."""
        self._file_discovery_strategies[name] = strategy_class

    def register_metadata_strategy(self, name: str, strategy_class: type) -> None:
        """Register a metadata strategy class."""
        self._metadata_strategies[name] = strategy_class

    def register_upload_strategy(self, name: str, strategy_class: type) -> None:
        """Register an upload strategy class."""
        self._upload_strategies[name] = strategy_class

    def register_data_unit_strategy(self, name: str, strategy_class: type) -> None:
        """Register a data unit strategy class."""
        self._data_unit_strategies[name] = strategy_class

    def create_validation_strategy(self, params: Dict[str, Any], context=None) -> ValidationStrategy:
        """Create validation strategy based on parameters."""
        strategy_name = params.get('validation_strategy', 'default')

        if strategy_name not in self._validation_strategies:
            # Import default strategy if not registered
            from .strategies.validation.default import DefaultValidationStrategy

            self.register_validation_strategy('default', DefaultValidationStrategy)
            strategy_name = 'default'

        strategy_class = self._validation_strategies[strategy_name]
        return strategy_class()

    def create_file_discovery_strategy(self, params: Dict[str, Any], context=None) -> FileDiscoveryStrategy:
        """Create file discovery strategy based on parameters."""
        is_recursive = params.get('is_recursive', True)
        strategy_name = 'recursive' if is_recursive else 'flat'

        if strategy_name not in self._file_discovery_strategies:
            # Import default strategies if not registered
            if strategy_name == 'recursive':
                from .strategies.file_discovery.recursive import RecursiveFileDiscoveryStrategy

                self.register_file_discovery_strategy('recursive', RecursiveFileDiscoveryStrategy)
            else:
                from .strategies.file_discovery.flat import FlatFileDiscoveryStrategy

                self.register_file_discovery_strategy('flat', FlatFileDiscoveryStrategy)

        strategy_class = self._file_discovery_strategies[strategy_name]
        return strategy_class()

    def create_metadata_strategy(self, params: Dict[str, Any], context=None) -> MetadataStrategy:
        """Create metadata strategy based on parameters."""
        # Always use Excel strategy for metadata processing
        # It will handle both specified paths and default meta.xlsx/meta.xls files
        strategy_name = 'excel'

        if strategy_name not in self._metadata_strategies:
            from .strategies.metadata.excel import ExcelMetadataStrategy

            self.register_metadata_strategy('excel', ExcelMetadataStrategy)

        strategy_class = self._metadata_strategies[strategy_name]
        return strategy_class()

    def create_upload_strategy(self, params: Dict[str, Any], context=None) -> UploadStrategy:
        """Create upload strategy (always uses synchronous upload for guaranteed ordering)."""
        if context is None:
            raise ValueError('Upload strategies require context parameter')

        # Always use sync upload to guarantee file order
        # This is critical for video frame extraction and PDF page extraction
        strategy_name = 'sync'

        if strategy_name not in self._upload_strategies:
            from .strategies.upload.sync import SyncUploadStrategy

            self.register_upload_strategy('sync', SyncUploadStrategy)

        strategy_class = self._upload_strategies[strategy_name]
        # Upload strategies always need context for client access
        return strategy_class(context)

    def create_data_unit_strategy(self, params: Dict[str, Any], context=None) -> DataUnitStrategy:
        """Create data unit strategy based on parameters."""
        if context is None:
            raise ValueError('Data unit strategies require context parameter')

        batch_size = params.get('creating_data_unit_batch_size', 1)
        strategy_name = 'batch' if batch_size > 1 else 'single'

        if strategy_name not in self._data_unit_strategies:
            # Import default strategies if not registered
            if strategy_name == 'batch':
                from .strategies.data_unit.batch import BatchDataUnitStrategy

                self.register_data_unit_strategy('batch', BatchDataUnitStrategy)
            else:
                from .strategies.data_unit.single import SingleDataUnitStrategy

                self.register_data_unit_strategy('single', SingleDataUnitStrategy)

        strategy_class = self._data_unit_strategies[strategy_name]
        # Data unit strategies always need context for client access
        return strategy_class(context)

    def get_available_strategies(self) -> Dict[str, list]:
        """Get all available strategy types and their registered names."""
        return {
            'validation': list(self._validation_strategies.keys()),
            'file_discovery': list(self._file_discovery_strategies.keys()),
            'metadata': list(self._metadata_strategies.keys()),
            'upload': list(self._upload_strategies.keys()),
            'data_unit': list(self._data_unit_strategies.keys()),
        }
