"""Domain model representing an ordered sequence of ActionSteps."""

from pydantic import BaseModel, Field
from .action_step import ActionStep


class ActionPlan(BaseModel):
    """
    a collection of ActionSteps that will be executed by the Executor service.

    Attributes:
        steps: a list of ActionSteps for the Executor to execute in sequential order.
    """

    steps: list[ActionStep] = Field(default_factory=list)
