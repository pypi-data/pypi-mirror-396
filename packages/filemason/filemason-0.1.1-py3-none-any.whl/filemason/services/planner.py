"""The planner service creates and outputs a list of action steps for the executor to perform."""

from pathlib import Path
from ..models.file_item import FileItem
from ..models.action_step import ActionStep, Action
from ..models.action_plan import ActionPlan


class Planner:
    """
    Service responsible for translating classified FileItems into an ordered
    ActionPlan describing how the files should be organized.

    The Planner is pure and side-effect free. It does not touch the filesystem.
    It simply determines the intended operations so that the Executor service
    can later perform them.
    """

    def create_plan(
        self,
        base_output_path: Path,
        files_list: list[FileItem],
        buckets: dict[str, list[str]],
    ) -> ActionPlan:
        """
        Build an ActionPlan consisting of directory-creation and file-move steps.

        This method takes a list of *classified* FileItems (i.e., FileItems whose
        `tags` field contains at least one bucket name) and constructs a sequence
        of ActionSteps describing how they should be organized under the given
        base output path.

        Two types of steps are generated:
            1. MKDIR steps:
                One directory-creation step is added for each bucket name defined
                in the configuration that is actually used by at least one
                classified file in `files_list`. These steps ensure that all target
                bucket folders exist before file-move steps execute.
            2. MOVE steps:
                For each classified FileItem, a move operation is added that will
                relocate the file from its current location (`file.path`) into the
                appropriate bucket directory under the base output path.

        The Planner does not perform any filesystem operations itself. It only
        constructs the plan that the Executor will execute later.

        Args:
            base_output_path (Path):
                The root directory under which all bucket folders and organized
                files should be placed.

            files_list (list[FileItem]):
                A list of FileItems that have already been classified by the
                Classifier service. Each FileItem should have at least one tag,
                where the first tag represents the assigned bucket.

            buckets (dict[str, list[str]]):
                Mapping of bucket names to lists of extensions, taken from the
                loaded configuration file. Only the keys (bucket names) are used
                here to generate MKDIR steps.

        Returns:
            ActionPlan:
                An ordered collection of ActionSteps describing all mkdir and
                move operations required to organize the files.

        """

        action_plan = ActionPlan(steps=[])
        seen_buckets: set[str] = {file.tags[0] for file in files_list}

        for bucket_name in buckets:
            if bucket_name in seen_buckets:
                step = ActionStep(
                    file_id=None,
                    action=Action.mkdir,
                    source=None,
                    destination=base_output_path / bucket_name,
                )
                action_plan.steps.append(step)

        for file in files_list:
            bucket = file.tags[0]
            step = ActionStep(
                file_id=file.id,
                action=Action.move,
                source=file.path,
                destination=base_output_path / bucket / file.path.name,
            )

            action_plan.steps.append(step)

        return action_plan
