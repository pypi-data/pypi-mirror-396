from filemason.services.classifier import Classifier
from filemason.services.executor import Executor
from filemason.services.planner import Planner
from filemason.services.reader import Reader
from filemason.orchestrator import Orchestrator


def test_orchestrator_dry_run(tmp_path):
    bucket_config = {"buckets": {"txt": ["txt"], "images": ["png"]}}
    reader = Reader()
    classifier = Classifier(bucket_config["buckets"])
    planner = Planner()
    executor = Executor()

    orchestrator = Orchestrator(reader, classifier, planner, executor, bucket_config)

    file_1 = tmp_path / "notes.txt"
    file_1.write_text("hello")

    file_2 = tmp_path / "pic.png"
    file_2.write_bytes(bytes(10))

    result = orchestrator.organize(tmp_path, dry_run=True)

    assert result.dry_run is True
    assert len(result.read_files) == 2
    assert len(result.classified_files) == 2
    assert len(result.action_plan.steps) > 0
    assert result.actions_taken == []


def test_orchestrator_execution(tmp_path):
    bucket_config = {"buckets": {"txt": ["txt"], "images": ["png"]}}
    reader = Reader()
    classifier = Classifier(bucket_config["buckets"])
    planner = Planner()
    executor = Executor()

    orchestrator = Orchestrator(reader, classifier, planner, executor, bucket_config)

    file_1 = tmp_path / "notes.txt"
    file_1.write_text("hello")

    file_2 = tmp_path / "pic.png"
    file_2.write_bytes(bytes(10))

    result = orchestrator.organize(tmp_path, dry_run=False)

    assert result.dry_run is False
    assert len(result.read_files) == 2
    assert len(result.classified_files) == 2
    assert len(result.action_plan.steps) == 4
