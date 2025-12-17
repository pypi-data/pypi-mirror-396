import json
from datetime import datetime
from pathlib import Path

from synapse_sdk.plugins.categories.upload.actions.upload import (
    ExcelSecurityConfig,
    PathAwareJSONEncoder,
)


class TestPathAwareJSONEncoder:
    """Test PathAwareJSONEncoder class."""

    def test_path_object_encoding(self):
        """Test encoding Path objects."""
        encoder = PathAwareJSONEncoder()
        path = Path('/test/path')
        result = encoder.default(path)
        assert result == '/test/path'

    def test_datetime_encoding(self):
        """Test encoding datetime objects."""
        encoder = PathAwareJSONEncoder()
        dt = datetime(2023, 1, 1, 12, 0, 0)
        result = encoder.default(dt)
        assert result == '2023-01-01T12:00:00'

    def test_string_with_fspath(self):
        """Test encoding objects with __fspath__ method."""
        encoder = PathAwareJSONEncoder()

        class MockPathLike:
            def __fspath__(self):
                return '/mock/path'

        obj = MockPathLike()
        result = encoder.default(obj)
        assert result == '/mock/path'

    def test_fallback_to_parent(self):
        """Test fallback to parent encoder for unknown objects."""
        encoder = PathAwareJSONEncoder()

        class UnknownObject:
            pass

        obj = UnknownObject()
        try:
            encoder.default(obj)
            assert False, 'Should have raised TypeError'
        except TypeError:
            pass

    def test_full_json_encoding(self):
        """Test full JSON encoding with mixed types."""
        data = {'path': Path('/test/path'), 'timestamp': datetime(2023, 1, 1), 'name': 'test'}
        result = json.dumps(data, cls=PathAwareJSONEncoder)
        expected = '{"path": "/test/path", "timestamp": "2023-01-01T00:00:00", "name": "test"}'
        assert result == expected


class TestExcelSecurityConfig:
    """Test ExcelSecurityConfig class."""

    def test_default_config_values(self):
        """Test default configuration values."""
        config = ExcelSecurityConfig()
        assert config.max_file_size_mb == 10
        assert config.max_file_size_bytes == 10 * 1024 * 1024
        assert config.max_rows == 100000
        assert config.max_columns == 50

        # Test backward compatibility properties
        assert config.MAX_FILE_SIZE_MB == 10
        assert config.MAX_FILE_SIZE_BYTES == 10 * 1024 * 1024
        assert config.MAX_ROWS == 100000
        assert config.MAX_COLUMNS == 50

    def test_from_action_config_with_values(self):
        """Test configuration creation from action config with values."""
        action_config = {'excel_config': {'max_file_size_mb': 20, 'max_rows': 50000, 'max_columns': 100}}
        config = ExcelSecurityConfig.from_action_config(action_config)
        assert config.max_file_size_mb == 20
        assert config.max_rows == 50000
        assert config.max_columns == 100

    def test_from_action_config_without_excel_config(self):
        """Test configuration creation from action config without excel_config."""
        action_config = {'other_config': 'value'}
        config = ExcelSecurityConfig.from_action_config(action_config)
        assert config.max_file_size_mb == 10  # default
        assert config.max_rows == 100000  # default
        assert config.max_columns == 50  # default

    def test_from_action_config_partial_values(self):
        """Test configuration creation with partial values."""
        action_config = {
            'excel_config': {
                'max_file_size_mb': 25,
                # max_rows and max_columns not specified
            }
        }
        config = ExcelSecurityConfig.from_action_config(action_config)
        assert config.max_file_size_mb == 25  # from config
        assert config.max_rows == 100000  # default
        assert config.max_columns == 50  # default
