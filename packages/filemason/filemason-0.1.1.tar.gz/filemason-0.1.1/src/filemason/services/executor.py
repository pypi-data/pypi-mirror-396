"""The Executor service takes an action plan and actually performs the actions in the file system."""

from ..models.action_plan import ActionPlan
from ..models.action_step import Action, ActionStep
from filemason.exceptions import MoveError
from filemason.models.failed_action import FailedAction


class Executor:
    """
    Execute the steps defined in an ActionPlan on the local file system.

    The Executor produces side effects, as it is responsible for creating
    directories and moving files. It does not validate business logic; it
    only performs the actions it is given and reports which steps succeeded
    or failed.
    """

    def handle(
        self, action_plan: ActionPlan
    ) -> tuple[list[ActionStep], list[FailedAction]]:
        """
        Handle a given action plan. This function iterates through an action plan's ActionSteps in order based on
        the ActionStep's Action attribute.

        Args:
        - action_plan(ActionPlan):
          An ActionPlan object that consists of ActionSteps.

        Returns:
        - A tuple consisting of 2 lists.
            - actions_taken: a list of actions that were taken successfully
            - failed_actions: a list of failed_actions containing the action step and the error/reason for failure.
        """
        actions_taken: list[ActionStep] = []
        failed_actions: list[FailedAction] = []
        for step in action_plan.steps:
            if step.action == Action.mkdir:
                try:
                    step.destination.mkdir(exist_ok=True)
                    actions_taken.append(step)
                except FileNotFoundError as e:
                    failed_actions.append(
                        FailedAction(
                            action_step=step,
                            error_type=type(e).__name__,
                            error_message=str(e),
                        )
                    )
                except PermissionError as e:
                    failed_actions.append(
                        FailedAction(
                            action_step=step,
                            error_type=type(e).__name__,
                            error_message=str(e),
                        )
                    )
                except OSError as e:
                    failed_actions.append(
                        FailedAction(
                            action_step=step,
                            error_type=type(e).__name__,
                            error_message=str(e),
                        )
                    )
            elif step.action == Action.move:
                if step.source is None:
                    raise ValueError("Move commands must have a valid source.")
                try:
                    if step.destination.exists():
                        failed_actions.append(
                            FailedAction(
                                action_step=step,
                                error_type=MoveError.__name__,
                                error_message="File of this name already exists in destination.",
                            )
                        )

                        continue
                    step.source.rename(step.destination)
                    actions_taken.append(step)
                except FileNotFoundError as e:
                    failed_actions.append(
                        FailedAction(
                            action_step=step,
                            error_type=type(e).__name__,
                            error_message=str(e),
                        )
                    )
                except PermissionError as e:
                    failed_actions.append(
                        FailedAction(
                            action_step=step,
                            error_type=type(e).__name__,
                            error_message=str(e),
                        )
                    )
                except OSError as e:
                    failed_actions.append(
                        FailedAction(
                            action_step=step,
                            error_type=type(e).__name__,
                            error_message=str(e),
                        )
                    )
        return actions_taken, failed_actions
