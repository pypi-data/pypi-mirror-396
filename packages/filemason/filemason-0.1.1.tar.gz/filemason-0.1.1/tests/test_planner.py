from filemason.models import action_plan
from filemason.models.action_step import Action
from pathlib import Path


def test_planner_happy_path(plan):

    assert isinstance(plan, action_plan.ActionPlan)
    assert len(plan.steps) > 0
    assert plan.steps[0].action == Action.mkdir
    assert isinstance(plan.steps[1].file_id, str)
    assert isinstance(plan.steps[1].destination, Path)


def test_planner_creates_mkdir_for_each_bucket(plan, buckets, basic_dir):
    mkdir_steps = [step for step in plan.steps if step.action is Action.mkdir]

    assert len(mkdir_steps) == len(buckets)

    for step in mkdir_steps:
        bucket_name = step.destination.relative_to(basic_dir).parts[0]
        assert bucket_name in buckets


def test_planner_with_no_files(planner, basic_dir, buckets):
    plan = planner.create_plan(
        base_output_path=basic_dir, files_list=[], buckets=buckets
    )

    mkdir_steps = [s for s in plan.steps if s.action is Action.mkdir]
    move_steps = [s for s in plan.steps if s.action is Action.move]

    assert len(mkdir_steps) == 0
    assert len(move_steps) == 0
