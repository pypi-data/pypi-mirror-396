from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, field_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.i18n import gettext as _
from synapse_sdk.utils.pydantic.validators import non_blank

from .utils import TargetHandlerFactory


class ExportParams(BaseModel):
    """Export action parameter validation model.

    Defines and validates all parameters required for export operations.
    Uses Pydantic for type validation and custom validators to ensure
    storage and filter resources exist before processing.

    Attributes:
        name (str): Human-readable name for the export operation
        description (str | None): Optional description of the export
        storage (int): Storage ID where exported data will be saved
        save_original_file (bool): Whether to save the original file
        path (str): File system path where exported data will be saved
        target (str): The target source to export data from (assignment, ground_truth, task)
        filter (dict): Filter criteria to apply when retrieving data
        extra_params (dict | None): Additional parameters for export customization.
            Example: {"include_metadata": True, "compression": "gzip"}

    Validation:
        - name: Must be non-blank after validation
        - storage: Must exist and be accessible via client API
        - target: Must be one of the supported target types
        - filter: Must be valid for the specified target type

    Example:
        >>> params = ExportParams(
        ...     name="Assignment Export",
        ...     storage=1,
        ...     path="/exports/assignments",
        ...     target="assignment",
        ...     filter={"project": 123}
        ... )
    """

    name: Annotated[str, AfterValidator(non_blank)]
    description: str | None = None
    storage: int
    save_original_file: bool = True
    path: str
    target: Literal['assignment', 'ground_truth', 'task']
    filter: dict
    extra_params: dict | None = None

    @field_validator('storage')
    @staticmethod
    def check_storage_exists(value, info):
        action = info.context['action']
        client = action.client
        try:
            client.get_storage(value)
        except ClientError:
            raise PydanticCustomError('client_error', _('Unable to get storage from Synapse backend.'))
        return value

    @field_validator('filter')
    @staticmethod
    def check_filter_by_target(value, info):
        action = info.context['action']
        client = action.client
        target = action.params['target']
        handler = TargetHandlerFactory.get_handler(target)
        return handler.validate_filter(value, client)
