"""Domain module for representing FileMason Job metadata."""

from filemason.models.file_item import FileItem
from filemason.models.action_step import ActionStep
from filemason.models.action_plan import ActionPlan
from filemason.models.failed_action import FailedAction
from pydantic import BaseModel, ConfigDict
from pathlib import Path


class RunResult(BaseModel):
    """
    Immutable snapshot capturing the complete outcome of a FileMason run.

    Attributes:
        source (Path): The directory that was organized.
        dry_run (bool): Whether this run was executed in dry-run mode.
        read_files (list[FileItem]): Files successfully read by the Reader service.
        skipped_files (list[tuple[Path, str]]): Files the Reader skipped, each paired with the reason.
        classified_files (list[FileItem]): Files that were successfully classified.
        unclassified_files (list[FileItem]): Files that could not be classified based on the config.
        action_plan (ActionPlan): The plan of actions generated for this job.
        actions_taken (list[ActionStep]): Actions successfully executed by the Executor.
        failed_actions (list[FailedAction]): Actions that failed, with the associated exception.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    source: Path
    dry_run: bool
    read_files: list[FileItem]
    skipped_files: list[tuple[Path, str]]
    classified_files: list[FileItem]
    unclassified_files: list[FileItem]
    action_plan: ActionPlan
    actions_taken: list[ActionStep]
    failed_actions: list[FailedAction]
