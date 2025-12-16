from pathlib import Path

import pytest

from filemason.models.file_item import FileItem


def test_basic_file_read(reader, basic_dir):
    files, skipped = reader.read_directory(basic_dir)
    assert len(files) == 1
    assert isinstance(files[0], FileItem)
    assert skipped == []
    assert files[0].path == basic_dir / "test.txt"


def test_multifile_dir_read(reader, multifile_dir):
    files, skipped = reader.read_directory(multifile_dir)
    assert len(files) == 2
    assert skipped == []
    assert files[0].path == multifile_dir / "test.txt"
    assert files[1].path == multifile_dir / "test2.txt"
    for item in files:
        assert isinstance(item, FileItem)


def test_dir_not_found(reader, tmp_path):
    missing_dir = tmp_path / "badinfo"
    with pytest.raises(NotADirectoryError):
        reader.read_directory(missing_dir)


def test_symlink_is_skipped(reader, symlink_dir):
    files, skipped = reader.read_directory(symlink_dir)
    skipped_path, reason = skipped[0]
    assert len(files) == 1
    assert len(skipped) == 1
    assert reason == "symlink skipped"
    assert skipped_path == symlink_dir / "link.txt"
    assert isinstance(reason, str)


def test_hidden_file_is_skipped(reader, hidden_file_dir):
    files, skipped = reader.read_directory(hidden_file_dir)
    skipped_path, reason = skipped[0]
    assert files == []
    assert len(skipped) == 1
    assert skipped_path == hidden_file_dir / ".gitignore"
    assert reason == "hidden file skipped"
    assert isinstance(reason, str)


def test_subdir_is_skipped(reader, directory_with_subdir):
    files, skipped = reader.read_directory(directory_with_subdir)
    skipped_path, reason = skipped[0]
    assert files == []
    assert len(skipped) == 1
    assert reason == "subdirectory skipped"


def test_dir_permission_errors(reader, directory, monkeypatch):

    def fake_iterdir(self):
        raise PermissionError("simulated permission error")

    monkeypatch.setattr(Path, "iterdir", fake_iterdir, raising=True)

    with pytest.raises(PermissionError) as excinfo:
        reader.read_directory(directory)

    assert "simulated permission error" in str(excinfo.value)


def test_file_permission_failure(reader, basic_dir, monkeypatch):

    def fake_create_path(file_path):
        raise PermissionError("simulated permission error")

    monkeypatch.setattr(reader, "_create_file", fake_create_path, raising=True)

    files, skipped = reader.read_directory(basic_dir)
    skipped_path, reason = skipped[0]
    assert files == []
    assert len(skipped) == 1
    assert "simulated permission error" in reason


def test_fifo_is_unrecognized(reader, fifo_dir):
    files, skipped = reader.read_directory(fifo_dir)
    skipped_path, reason = skipped[0]
    assert reason == "Unrecognized item"
