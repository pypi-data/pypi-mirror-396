"""Classifies a given list of FileItems."""

from typing import Dict, List
from ..models.file_item import FileItem


class Classifier:
    """
    Classifies FileItems into buckets based on extension.

    The classifier uses an inverted mapping of extension → bucket for
    O(1) lookup during classification.
    """

    def __init__(self, buckets: Dict[str, list[str]]):
        """Initialize the classifier with a bucket configuration.

        Args:
            buckets: A dictionary mapping bucket names to lists of extensions.
        """
        self.ext_to_buckets: Dict[str, str] = invert_bucket_dict(buckets)

    def classify(
        self, file_list: List[FileItem]
    ) -> tuple[list[FileItem], list[FileItem]]:
        """
        Normalizes and classifies each FileItem in the list of FileItems provided by the Reader service.

        Args:
            file_list: A list of FileItems

        Returns:
            A tuple containing:
                classified_list: A list of new FileItems with their appropriate buckets assigned to the FileItem.tags property.
                unclassified_list: A list of new FileItems with no tags due to the extension not being listed in the configuration file.
        """
        classified_list = []
        unclassified_list = []

        for file in file_list:
            extension = file.extension.lower().lstrip(".")

            bucket = self.ext_to_buckets.get(extension)
            if bucket is None:
                unclassified_list.append(file)
            else:
                classified_list.append(file.with_tag(bucket))

        return classified_list, unclassified_list


def invert_bucket_dict(buckets: Dict[str, list]) -> dict[str, str]:
    """Invert the bucket dictionary for fast extension lookup.

    Args:
        buckets: Mapping of bucket names to lists of extensions.

    Returns:
        A dictionary mapping normalized extensions to their bucket names.
    """
    inverted: Dict[str, str] = {}

    for bucket_name, extensions in buckets.items():
        for extension in extensions:
            inverted[extension.lower()] = bucket_name

    return inverted
