"""Orchestrator module for coordinating the full FileMason workflow."""

from filemason.services.classifier import Classifier
from filemason.services.executor import Executor
from filemason.services.planner import Planner
from filemason.services.reader import Reader
from filemason.models.run_result import RunResult
from pathlib import Path


class Orchestrator:
    """
    Coordinates the full FileMason pipeline for organizing a directory.

    This class wires together the Reader, Classifier, Planner, and Executor
    services to perform a complete run and returns a `RunResult` snapshot.
    """

    def __init__(
        self,
        reader: Reader,
        classifier: Classifier,
        planner: Planner,
        executor: Executor,
        config: dict,
    ):
        """
        Initialize a new Orchestrator instance.

        Args:
            reader (Reader): Service responsible for scanning directories and
                collecting file metadata.
            classifier (Classifier): Service that assigns bucket tags to files
                based on the configuration.
            planner (Planner): Service that builds an `ActionPlan` from the
                classified files.
            executor (Executor): Service that executes the generated
                `ActionPlan`.
            config (dict): Configuration dictionary used by the pipeline,
                expected to contain a ``"buckets"`` mapping for classification.
        """

        self.reader = reader
        self.classifier = classifier
        self.planner = planner
        self.executor = executor
        self.config = config

    def organize(self, directory: Path, dry_run: bool = True) -> RunResult:
        """
        Run the full FileMason workflow against a directory.

        The pipeline consists of:
        1. Reading files from the given directory.
        2. Classifying files into buckets.
        3. Generating an action plan.
        4. Optionally executing the plan (when not in dry-run mode).

        Args:
            directory (Path): The directory to organize.
            dry_run (bool): If True, no filesystem changes are performed and
                the executor is skipped. Defaults to True.

        Returns:
            RunResult: An immutable snapshot describing the outcome of the run,
            including read, classified, and skipped files, the generated
            action plan, and any actions taken or failed.
        """

        read_files, skipped_files = self.reader.read_directory(directory)
        classified_files, unclassified_files = self.classifier.classify(read_files)
        action_plan = self.planner.create_plan(
            directory, classified_files, self.config["buckets"]
        )

        if dry_run:
            return RunResult(
                source=directory.absolute(),
                dry_run=dry_run,
                read_files=read_files,
                skipped_files=skipped_files,
                classified_files=classified_files,
                unclassified_files=unclassified_files,
                action_plan=action_plan,
                actions_taken=[],
                failed_actions=[],
            )

        successful_steps, failed_steps = self.executor.handle(action_plan)
        return RunResult(
            source=directory.absolute(),
            dry_run=dry_run,
            read_files=read_files,
            skipped_files=skipped_files,
            classified_files=classified_files,
            unclassified_files=unclassified_files,
            action_plan=action_plan,
            actions_taken=successful_steps,
            failed_actions=failed_steps,
        )
