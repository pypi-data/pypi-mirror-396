from filemason.models.action_plan import ActionPlan
from filemason.models.action_step import ActionStep, Action
from filemason.services.executor import Executor
from filemason.models.failed_action import FailedAction
import pytest
from pathlib import Path


@pytest.fixture
def basic_executor_plan(tmp_path):
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()

    src = source_dir / "file.txt"
    src.write_text("hello")

    dest = dest_dir / "file.txt"

    plan = ActionPlan(
        steps=[
            ActionStep(
                file_id="123",
                action=Action.move,
                source=src,
                destination=dest,
            )
        ]
    )

    return src, dest, plan


@pytest.fixture
def mkdir_executor_plan(tmp_path):
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()

    dest = dest_dir / "file.txt"

    plan = ActionPlan(
        steps=[
            ActionStep(
                file_id="123",
                action=Action.mkdir,
                source=None,
                destination=dest,
            )
        ]
    )

    return plan


@pytest.fixture
def basic_executor_plan_with_no_source(tmp_path):
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()

    src = None

    dest = dest_dir / "file.txt"

    plan = ActionPlan(
        steps=[
            ActionStep(
                file_id="123",
                action=Action.move,
                source=src,
                destination=dest,
            )
        ]
    )

    return src, dest, plan


def test_executor_moves_file_successfully(basic_executor_plan):
    src, dest, plan = basic_executor_plan

    handled, bad = Executor().handle(plan)

    assert len(handled) == 1
    assert not bad
    assert not src.exists()
    assert dest.exists()
    assert dest.read_text() == "hello"


def test_executor_makes_dirs_successfully(mkdir_executor_plan):
    plan = mkdir_executor_plan

    handled, unhandled = Executor().handle(plan)

    assert handled[0].action == Action.mkdir
    assert handled[0].source is None
    assert unhandled == []


def test_src_deleted_during_move(basic_executor_plan, monkeypatch):
    src, dest, plan = basic_executor_plan

    def return_fnf(self, target):
        raise FileNotFoundError("fake error")

    monkeypatch.setattr(Path, "rename", return_fnf)

    handled, unhandled = Executor().handle(plan)

    assert handled == []
    assert len(unhandled) == 1
    assert unhandled[0].error_type == "FileNotFoundError"


def test_file_already_exists(basic_executor_plan, monkeypatch):
    src, dest, plan = basic_executor_plan

    def file_exists(self):
        return True

    monkeypatch.setattr(Path, "exists", file_exists)

    handled, unhandled = Executor().handle(plan)

    assert isinstance(unhandled[0], FailedAction)
    assert unhandled[0].error_type == "MoveError"
    assert handled == []


def test_no_permissions_to_file(basic_executor_plan, monkeypatch):
    src, dest, plan = basic_executor_plan

    def PermsError(self, target):
        raise PermissionError("you shall not pass")

    monkeypatch.setattr(Path, "rename", PermsError)

    handled, unhandled = Executor().handle(plan)

    assert isinstance(unhandled[0], FailedAction)
    assert handled == []


def test_OS_error_with_file(basic_executor_plan, monkeypatch):
    src, dest, plan = basic_executor_plan

    def op_sys_error(self, target):
        raise OSError("PEBCAK issue incoming")

    monkeypatch.setattr(Path, "rename", op_sys_error)

    handled, unhandled = Executor().handle(plan)

    assert isinstance(unhandled[0], FailedAction)
    assert handled == []


def test_source_is_none(basic_executor_plan_with_no_source):

    src, dest, plan = basic_executor_plan_with_no_source

    with pytest.raises(ValueError):
        handled, unhandled = Executor().handle(plan)


def test_dir_not_found(mkdir_executor_plan, monkeypatch):
    plan = mkdir_executor_plan

    def dir_deleted(*args, **kwargs):
        raise FileNotFoundError("file not found")

    monkeypatch.setattr(Path, "mkdir", dir_deleted)

    handled, unhandled = Executor().handle(plan)

    assert isinstance(unhandled[0], FailedAction)
    assert handled == []


def test_no_permissions_to_dir(mkdir_executor_plan, monkeypatch):
    plan = mkdir_executor_plan

    def PermError(*args, **kwargs):
        raise PermissionError("you shall not pass")

    monkeypatch.setattr(Path, "mkdir", PermError)

    handled, unhandled = Executor().handle(plan)

    assert isinstance(unhandled[0], FailedAction)
    assert handled == []


def test_OS_issue_with_dir(mkdir_executor_plan, monkeypatch):
    plan = mkdir_executor_plan

    def PermError(*args, **kwargs):
        raise OSError("PEBCAK issue inbound")

    monkeypatch.setattr(Path, "mkdir", PermError)

    handled, unhandled = Executor().handle(plan)

    assert isinstance(unhandled[0], FailedAction)
    assert handled == []
