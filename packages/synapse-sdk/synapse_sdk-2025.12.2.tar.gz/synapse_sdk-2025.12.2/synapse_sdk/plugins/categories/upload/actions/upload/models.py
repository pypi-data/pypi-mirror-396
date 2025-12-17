from typing import Annotated

from pydantic import AfterValidator, BaseModel, ValidationInfo, field_validator, model_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.utils.pydantic.validators import non_blank

from .enums import VALIDATION_ERROR_MESSAGES, ValidationErrorCode


class AssetConfig(BaseModel):
    """Configuration for individual asset in multi-path mode.

    Used when use_single_path=False to specify unique paths and recursive
    settings for each file specification.

    Attributes:
        path: File system path for this specific asset.
        is_recursive: Whether to recursively search subdirectories for this
            asset. Defaults to True.

    Examples:
        >>> asset_config = AssetConfig(
        ...     path="/sensors/camera/front",
        ...     is_recursive=True
        ... )
    """

    path: str
    is_recursive: bool = True


class UploadParams(BaseModel):
    """Upload action parameter validation model.

    Defines and validates all parameters required for upload operations.
    Uses Pydantic for type validation and custom validators to ensure
    storage, data_collection, and project resources exist before processing.

    The model supports two operational modes controlled by the use_single_path
    flag:

    Single Path Mode (use_single_path=True, DEFAULT):
        Traditional mode where all file specifications share one base path.
        Requires 'path' parameter. Ignores 'assets' parameter.

    Multi-Path Mode (use_single_path=False):
        Advanced mode where each file specification has its own path.
        Requires 'assets' parameter. Ignores 'path' and 'is_recursive' parameters.

    Attributes:
        name: Human-readable name for the upload operation. Must be non-blank.
        description: Optional description of the upload operation.
        use_single_path: Mode selector. True for single path mode, False for
            multi-path mode. Defaults to True.
        path: Base path for single path mode. Required when use_single_path=True.
        is_recursive: Global recursive setting for single path mode.
            Defaults to True.
        assets: Per-asset path configurations for multi-path mode. Dictionary
            mapping file specification names to AssetConfig objects. Required
            when use_single_path=False.
        storage: Storage ID where files will be uploaded. Must exist and be
            accessible via client API.
        data_collection: Data collection ID for organizing uploads. Must exist
            and be accessible via client API.
        project: Optional project ID for grouping. Must exist if specified.
        excel_metadata_path: Path to Excel metadata file. Can be:
            - Absolute path: '/data/metadata.xlsx'
            - Relative to storage default path: 'metadata.xlsx'
            - Relative to working directory (single-path mode): 'metadata.xlsx'
        max_file_size_mb: Maximum file size limit in megabytes. Defaults to 50.
        creating_data_unit_batch_size: Batch size for data unit creation.
            Defaults to 1.
        use_async_upload: Whether to use asynchronous upload processing.
            Defaults to True.
        extra_params: Extra parameters for the action. Optional.

    Examples:
        Single Path Mode (Traditional):

            >>> params = UploadParams(
            ...     name="Standard Upload",
            ...     use_single_path=True,
            ...     path="/data/experiment_1",
            ...     is_recursive=True,
            ...     storage=1,
            ...     data_collection=5
            ... )

        Multi-Path Mode (Advanced):

            >>> params = UploadParams(
            ...     name="Multi-Source Upload",
            ...     use_single_path=False,
            ...     assets={
            ...         "image_1": AssetConfig(path="/sensors/camera", is_recursive=True),
            ...         "pcd_1": AssetConfig(path="/sensors/lidar", is_recursive=False)
            ...     },
            ...     storage=1,
            ...     data_collection=5
            ... )

        With Excel Metadata:

            >>> params = UploadParams(
            ...     name="Upload with Metadata",
            ...     path="/data/files",
            ...     storage=1,
            ...     data_collection=5,
            ...     excel_metadata_path="metadata.xlsx"
            ... )
    """

    name: Annotated[str, AfterValidator(non_blank)]
    description: str | None = None

    # Mode selector flag (True = single path mode, False = multi-path mode)
    use_single_path: bool = True

    # Single path mode fields (used when use_single_path=True)
    path: str | None = None
    is_recursive: bool = True

    # Multi-path mode fields (used when use_single_path=False)
    assets: dict[str, AssetConfig] | None = None

    storage: int
    data_collection: int
    project: int | None = None

    # Excel metadata file path (absolute or relative to working directory)
    excel_metadata_path: str | None = None

    max_file_size_mb: int = 50
    creating_data_unit_batch_size: int = 1
    extra_params: dict | None = None

    @field_validator('storage', mode='before')
    @classmethod
    def check_storage_exists(cls, value, info: ValidationInfo) -> int:
        if info.context is None:
            error_code = ValidationErrorCode.MISSING_CONTEXT
            raise PydanticCustomError(error_code.value, VALIDATION_ERROR_MESSAGES[error_code])

        action = info.context['action']
        client = action.client
        try:
            client.get_storage(value)
        except ClientError as e:
            error_code = ValidationErrorCode.STORAGE_NOT_FOUND
            error_message = VALIDATION_ERROR_MESSAGES[error_code].format(value, str(e))
            raise PydanticCustomError(error_code.value, error_message)
        return value

    @field_validator('data_collection', mode='before')
    @classmethod
    def check_data_collection_exists(cls, value, info: ValidationInfo) -> int:
        if info.context is None:
            error_code = ValidationErrorCode.MISSING_CONTEXT
            raise PydanticCustomError(error_code.value, VALIDATION_ERROR_MESSAGES[error_code])

        action = info.context['action']
        client = action.client
        try:
            client.get_data_collection(value)
        except ClientError as e:
            error_code = ValidationErrorCode.DATA_COLLECTION_NOT_FOUND
            error_message = VALIDATION_ERROR_MESSAGES[error_code].format(value, str(e))
            raise PydanticCustomError(error_code.value, error_message)
        return value

    @field_validator('project', mode='before')
    @classmethod
    def check_project_exists(cls, value, info: ValidationInfo) -> int | None:
        if not value:
            return value

        if info.context is None:
            error_code = ValidationErrorCode.MISSING_CONTEXT
            raise PydanticCustomError(error_code.value, VALIDATION_ERROR_MESSAGES[error_code])

        action = info.context['action']
        client = action.client
        try:
            client.get_project(value)
        except ClientError as e:
            error_code = ValidationErrorCode.PROJECT_NOT_FOUND
            error_message = VALIDATION_ERROR_MESSAGES[error_code].format(value, str(e))
            raise PydanticCustomError(error_code.value, error_message)
        return value

    @model_validator(mode='after')
    def validate_path_configuration(self) -> 'UploadParams':
        """Validate path configuration based on use_single_path mode."""
        if self.use_single_path:
            # Single path mode: requires path
            if not self.path:
                raise PydanticCustomError(
                    'missing_path', "When use_single_path=true (single path mode), 'path' is required"
                )
            # Warn if assets is provided in single path mode (it will be ignored)
            # For now, we'll silently ignore it
        else:
            # Multi-path mode: requires assets
            if not self.assets:
                raise PydanticCustomError(
                    'missing_assets',
                    "When use_single_path=false (multi-path mode), 'assets' must be provided "
                    'with path configurations for each file specification',
                )
            # path and is_recursive are ignored in multi-path mode

        return self
