import json
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, model_validator


class PathAwareJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Path objects and datetime objects.

    Extends the default JSON encoder to properly serialize Path objects
    and datetime objects that are commonly used in upload operations.

    Supported object types:
    - Path objects (converts to string using __fspath__ or as_posix)
    - Datetime objects (converts using isoformat)
    - All other standard JSON-serializable types

    Example:
        >>> data = {"path": Path("/tmp/file.txt"), "timestamp": datetime.now()}
        >>> json.dumps(data, cls=PathAwareJSONEncoder)
        '{"path": "/tmp/file.txt", "timestamp": "2023-01-01T12:00:00"}'
    """

    def default(self, obj):
        if hasattr(obj, '__fspath__'):
            return obj.__fspath__()
        elif hasattr(obj, 'as_posix'):
            return obj.as_posix()
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super().default(obj)


class ExcelSecurityConfig(BaseModel):
    """Security configuration for Excel file processing using Pydantic.

    Defines essential security limits for Excel file processing to prevent
    resource exhaustion attacks and ensure safe handling of potentially malicious files.

    Attributes:
        max_file_size_mb (int): Maximum file size in megabytes (default: 10)
        max_rows (int): Maximum number of rows allowed (default: 100000)
        max_columns (int): Maximum number of columns allowed (default: 50)
    """

    max_file_size_mb: int = Field(
        default=10,
        ge=1,
        le=1000,
        description='Maximum file size in megabytes',
    )

    max_rows: int = Field(
        default=100000,
        ge=1,
        le=100000,
        description='Maximum number of rows allowed',
    )

    max_columns: int = Field(
        default=50,
        ge=1,
        le=16384,  # Excel's column limit
        description='Maximum number of columns allowed',
    )

    max_memory_usage_mb: int = Field(
        default=30,
        ge=1,
        le=1000,
        description='Maximum memory usage in megabytes',
    )

    max_filename_length: int = Field(
        default=255,
        ge=1,
        le=1000,
        description='Maximum filename length',
    )

    max_column_name_length: int = Field(
        default=100,
        ge=1,
        le=500,
        description='Maximum column name length',
    )

    max_metadata_value_length: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description='Maximum metadata value length',
    )

    validation_check_interval: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description='Validation check interval for processing',
    )

    model_config = {'validate_assignment': True, 'extra': 'forbid'}

    @model_validator(mode='after')
    def validate_resource_limits(self) -> 'ExcelSecurityConfig':
        """Validate that resource limits are reasonable."""
        # Check for unreasonable combinations
        estimated_cells = self.max_rows * self.max_columns
        if estimated_cells > 50000000:  # 50 million cells
            raise ValueError(
                f'Combination of max_rows ({self.max_rows}) and max_columns ({self.max_columns}) '
                f'would allow too many cells ({estimated_cells:,})'
            )

        return self

    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def max_memory_usage_bytes(self) -> int:
        """Get maximum memory usage in bytes."""
        return self.max_memory_usage_mb * 1024 * 1024

    # Backward compatibility properties (uppercase versions)
    @property
    def MAX_FILE_SIZE_MB(self) -> int:
        """Backward compatibility property."""
        return self.max_file_size_mb

    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        """Backward compatibility property."""
        return self.max_file_size_bytes

    @property
    def MAX_MEMORY_USAGE_MB(self) -> int:
        """Backward compatibility property."""
        return self.max_memory_usage_mb

    @property
    def MAX_MEMORY_USAGE_BYTES(self) -> int:
        """Backward compatibility property."""
        return self.max_memory_usage_bytes

    @property
    def MAX_ROWS(self) -> int:
        """Backward compatibility property."""
        return self.max_rows

    @property
    def MAX_COLUMNS(self) -> int:
        """Backward compatibility property."""
        return self.max_columns

    @property
    def MAX_FILENAME_LENGTH(self) -> int:
        """Backward compatibility property."""
        return self.max_filename_length

    @property
    def MAX_COLUMN_NAME_LENGTH(self) -> int:
        """Backward compatibility property."""
        return self.max_column_name_length

    @property
    def MAX_METADATA_VALUE_LENGTH(self) -> int:
        """Backward compatibility property."""
        return self.max_metadata_value_length

    @property
    def VALIDATION_CHECK_INTERVAL(self) -> int:
        """Backward compatibility property."""
        return self.validation_check_interval

    @classmethod
    def from_action_config(cls, action_config: Optional[Dict[str, Any]]) -> 'ExcelSecurityConfig':
        """Create ExcelSecurityConfig from plugin action configuration (config.yaml).

        Args:
            action_config: Action configuration dictionary from config.yaml

        Returns:
            New ExcelSecurityConfig instance with config.yaml values

        Example config.yaml:
            actions:
              upload:
                excel_config:
                  max_file_size_mb: 25
                  max_rows: 50000
                  max_columns: 100
        """
        if not action_config or 'excel_config' not in action_config:
            return cls()

        excel_config = action_config['excel_config']

        return cls(
            max_file_size_mb=excel_config.get('max_file_size_mb', 10),
            max_rows=excel_config.get('max_rows', 100000),
            max_columns=excel_config.get('max_columns', 50),
            max_memory_usage_mb=excel_config.get('max_memory_usage_mb', 30),
            max_filename_length=excel_config.get('max_filename_length', 255),
            max_column_name_length=excel_config.get('max_column_name_length', 100),
            max_metadata_value_length=excel_config.get('max_metadata_value_length', 1000),
            validation_check_interval=excel_config.get('validation_check_interval', 1000),
        )


class ExcelMetadataUtils:
    """Utility class for Excel metadata processing."""

    def __init__(self, config: ExcelSecurityConfig):
        """Initialize with Excel security configuration."""
        self.config = config

    def is_valid_filename_length(self, filename: str) -> bool:
        """Check if filename length is within limits."""
        return len(filename) <= self.config.max_filename_length

    def validate_and_truncate_string(self, value: str, max_length: int) -> str:
        """Validate and truncate string to maximum length."""
        if not isinstance(value, str):
            value = str(value)

        # Strip whitespace
        value = value.strip()

        # Truncate if too long
        if len(value) > max_length:
            value = value[:max_length]

        return value

    def is_valid_column_name(self, column_name: str) -> bool:
        """Check if column name is valid."""
        if not column_name or not isinstance(column_name, str):
            return False
        return len(column_name.strip()) <= self.config.max_column_name_length

    def is_valid_metadata_value(self, value: str) -> bool:
        """Check if metadata value is valid."""
        if value is None:
            return True
        if not isinstance(value, str):
            value = str(value)
        return len(value) <= self.config.max_metadata_value_length
