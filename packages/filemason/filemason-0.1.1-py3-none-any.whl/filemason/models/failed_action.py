from pydantic import BaseModel, ConfigDict
from filemason.models.action_step import ActionStep


class FailedAction(BaseModel):

    model_config = ConfigDict(frozen=True, extra="forbid")
    action_step: ActionStep
    error_type: str
    error_message: str
