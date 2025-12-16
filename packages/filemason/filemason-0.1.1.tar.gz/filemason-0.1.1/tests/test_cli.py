import pytest
from typer.testing import CliRunner
from filemason.cli import app, main
from importlib.metadata import PackageNotFoundError


runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
    assert "organize" in result.stdout
    assert "get-plan" in result.stdout or "get_plan" in result.stdout


def test_get_plan(basic_dir):
    result = runner.invoke(app, ["get-plan", str(basic_dir)])
    assert result.exit_code == 0
    assert "Action Plan" in result.stdout
    assert "Step" in result.stdout
    assert "File ID" in result.stdout
    assert "Action" in result.stdout
    assert "Source" in result.stdout
    assert "Destination" in result.stdout


def test_organize_dry(basic_dir):
    result = runner.invoke(app, ["organize", str(basic_dir)])
    assert result
    assert "Dry run" in result.stdout
    assert "Files read" in result.stdout
    assert "Result" in result.stdout
    assert "Count" in result.stdout


def test_organize_no_dry(basic_dir):
    result = runner.invoke(app, ["organize", "--no-dry", str(basic_dir)])
    assert "Dry run" in result.stdout
    assert "Files read" in result.stdout
    assert "Result" in result.stdout
    assert "Count" in result.stdout


def test_main_runs(monkeypatch):
    monkeypatch.setattr("sys.argv", ["filemason", "--help"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


def test_organize_dir_does_not_exist():
    result = runner.invoke(app, ["organize", "--no-dry", "/bad/path/to/dir"])
    assert result.exit_code == 1
    assert "Directory does not exist" in result.stdout


def test_get_plan_dir_does_not_exist():
    result = runner.invoke(app, ["get-plan", "/bad/path/to/dir/two"])
    assert result.exit_code == 1
    assert "Directory does not exist" in result.stdout


def test_version():
    result = runner.invoke(app, ["version"])

    assert "0.1.0" in result.stdout


def package_not_found(name):
    raise PackageNotFoundError


def test_version_error(monkeypatch):

    monkeypatch.setattr("filemason.cli.get_version", package_not_found)
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "filemason 0.0.0" in result.stdout
