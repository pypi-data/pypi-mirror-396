from typing import Annotated, Any, Dict, Optional

from pydantic import AfterValidator, BaseModel, field_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.backend.models import JobStatus
from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.plugins.categories.upload.actions.upload.enums import VALIDATION_ERROR_MESSAGES, ValidationErrorCode
from synapse_sdk.shared.enums import Context
from synapse_sdk.utils.pydantic.validators import non_blank

from .enums import AnnotateTaskDataStatus


class ToTaskParams(BaseModel):
    """ToTask action parameters.

    Args:
        name (str): The name of the action.
        description (str | None): The description of the action.
        project (int): The project ID.
        agent (int): The agent ID.
        task_filters (dict): The filters of tasks.
        method (AnnotationMethod): The method of annotation.
        target_specification_name (str | None): The name of the target specification.
        model (int): The model ID.
        pre_processor (int | None): The pre processor ID.
        pre_processor_params (dict): The params of the pre processor.
    """

    name: Annotated[str, AfterValidator(non_blank)]
    description: Optional[str] = None
    project: int
    agent: int
    task_filters: Dict[str, Any]
    method: Optional[str] = None
    target_specification_name: Optional[str] = None
    model: Optional[int] = None
    pre_processor: Optional[int] = None
    pre_processor_params: Dict[str, Any]

    @field_validator('project', mode='before')
    @classmethod
    def check_project_exists(cls, value: int, info) -> int:
        """Validate synapse-backend project exists."""
        if not value:
            return value

        action = info.context['action']
        client = action.client
        try:
            client.get_project(value)
        except ClientError as e:
            error_code = ValidationErrorCode.PROJECT_NOT_FOUND
            error_message = VALIDATION_ERROR_MESSAGES[error_code].format(value, str(e))
            raise PydanticCustomError(error_code.value, error_message)
        return value


class ToTaskResult(BaseModel):
    """Result model for ToTaskAction.start method.

    Args:
        status (JobStatus): The job status from the action execution.
        message (str): A descriptive message about the action result.
    """

    status: JobStatus
    message: str

    def model_dump(self, **kwargs):
        """Override model_dump to return status as enum value."""
        data = super().model_dump(**kwargs)
        if 'status' in data and isinstance(data['status'], JobStatus):
            data['status'] = data['status'].value
        return data


class AnnotateTaskEventLog(BaseModel):
    """Annotate task event log model."""

    info: Optional[str] = None
    status: Context
    created: str


class AnnotateTaskDataLog(BaseModel):
    """Log model for annotate task data."""

    task_info: Optional[str] = None
    status: AnnotateTaskDataStatus
    created: str


class MetricsRecord(BaseModel):
    """Metrics record model."""

    stand_by: int
    failed: int
    success: int
