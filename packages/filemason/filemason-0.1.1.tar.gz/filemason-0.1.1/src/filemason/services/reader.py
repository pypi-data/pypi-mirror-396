"""Reader service for scanning directories and returning file metadata."""

from datetime import datetime, timezone
from pathlib import Path

from ..models.file_item import FileItem


class Reader:
    """
    Read files from a directory and return FileItem objects.

    Skips hidden files, symlinks, and subdirectories, and tracks skipped
    items along with their associated reasons.
    """

    def read_directory(
        self, directory: Path | str
    ) -> tuple[list[FileItem], list[tuple[Path, str]]]:
        """
        Read all files in a directory, skipping hidden files, symlinks, and subdirectories.

        Args:
        directory (Path | str): Path of the directory to read.

        Returns:
        tuple:
            - list[FileItem]: Files successfully read from the directory.
            - list[tuple[Path, str]]: Skipped items and the reason each was skipped.

        Raises:
        NotADirectoryError: If the given path is not a directory.
        PermissionError, FileNotFoundError, OSError: If reading the directory fails.
        """

        directory = Path(directory)
        file_list: list[FileItem] = []
        skipped: list[tuple[Path, str]] = []
        # check if given path is a directory
        if not directory.is_dir():
            raise NotADirectoryError(f"{directory} is not a directory.")

        # try to read the items in the directory
        try:
            entities = sorted(directory.iterdir(), key=lambda item: item.name.lower())
        except (PermissionError, FileNotFoundError, OSError):
            raise

        for item in entities:
            if item.name.startswith("."):
                skipped.append((item, "hidden file skipped"))
                continue
            elif item.is_symlink():
                skipped.append((item, "symlink skipped"))
            elif item.is_dir():
                skipped.append((item, "subdirectory skipped"))
            elif item.is_file():
                try:
                    file_list.append(self._create_file(item))
                except (PermissionError, FileNotFoundError, OSError) as e:
                    skipped.append((item, f"{type(e).__name__}: {e}"))
                    continue
            else:
                skipped.append((item, "Unrecognized item"))
        return file_list, skipped

    def _create_file(self, file: Path) -> FileItem:
        """
        Create a FileItem object from a given Path.

        Args:
        - file (Path): The file to convert.

        Returns:
        - FileItem: An object containing metadata about the file (name, path, extension, size, timestamps).
        """

        stats = file.stat()
        extension = ".".join(s.lstrip(".") for s in file.suffixes).lower()
        file_name = file.stem
        file_path = file.resolve(strict=False)
        file_extension = extension
        file_size = stats.st_size
        file_last_modified = datetime.fromtimestamp(
            stats.st_mtime, tz=timezone.utc
        ).replace(microsecond=0)
        file_created = datetime.fromtimestamp(stats.st_ctime, tz=timezone.utc).replace(
            microsecond=0
        )
        return FileItem(
            name=file_name,
            path=file_path,
            extension=file_extension,
            size=file_size,
            last_modified=file_last_modified,
            created=file_created,
        )
