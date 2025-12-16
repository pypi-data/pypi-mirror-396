"""Read, validate, and cache the application's configuration file."""

import tomllib
from pathlib import Path
from typing import Any, Dict, List

from filemason.exceptions import (
    ConfigFileError,
    ConfigParseError,
    ConfigValidationError,
)

_config_cache: Dict[str, Any] | None = None

config_path: Path = Path(__file__).with_name("config.toml")


def load_config() -> Dict[str, Any]:
    """Load, validate, and cache the application's configuration.

    If a configuration has already been loaded, the cached version is returned.

    Returns:
        The parsed and validated configuration dictionary.

    Raises:
        ConfigFileError: If the configuration file cannot be found or read.
        ConfigParseError: If the TOML content is invalid.
        ConfigValidationError: If the bucket configuration violates required policies.
    """

    global _config_cache

    if _config_cache is not None:
        return _config_cache

    try:
        with open(config_path, "rb") as file:
            config_data: Dict[str, Any] = tomllib.load(file)

    except tomllib.TOMLDecodeError as e:
        raise ConfigParseError(f"Invalid TOML format in {config_path}: {e}") from e
    except PermissionError as e:
        raise ConfigFileError(
            f"Insufficient permissions to read {config_path}: {e}"
        ) from e
    except FileNotFoundError as e:
        raise ConfigFileError(
            f"Config file cannot be found at {config_path}: {e}"
        ) from e
    except OSError as e:
        raise ConfigFileError(f"Unable to read config file {config_path}: {e}") from e

    if "buckets" not in config_data:
        raise ConfigValidationError(f"Missing [buckets] table in {config_path}")

    _validate_bucket_config(config_data["buckets"])

    _config_cache = config_data

    return _config_cache


def _validate_bucket_config(buckets: Dict[str, List[str]]) -> None:
    """Validate the bucket configuration against required policies.

    Policies enforced:
        1. Buckets cannot be empty.
        2. Extensions cannot appear in multiple buckets or be duplicated within a bucket.

    Args:
        buckets: Mapping of bucket names to lists of file extensions.

    Raises:
        ConfigValidationError: If any bucket is empty or if duplicate extensions are detected.
    """
    inverted_bucket: Dict[str, List[str]] = {}
    duplicate_extensions: Dict[str, List[str]] = {}
    empty_buckets = []

    for bucket, extensions in buckets.items():

        if not extensions:
            empty_buckets.append(bucket)

        for extension in extensions:
            normalized = extension.lower().lstrip(".")
            if normalized not in inverted_bucket:
                inverted_bucket[normalized] = [bucket]
            else:
                inverted_bucket[normalized].append(bucket)
                duplicate_extensions[normalized] = inverted_bucket[normalized]

    if empty_buckets:
        if len(empty_buckets) == 1:
            raise ConfigValidationError(f"Bucket {empty_buckets[0]} cannot be empty.")
        else:
            empty_buckets_list = ", ".join(empty_buckets)
            raise ConfigValidationError(
                f"Buckets {empty_buckets_list} cannot be empty."
            )

    if duplicate_extensions:
        duplicate_details = "\n".join(
            f"- {extension} found in {', '.join(bucket_list)}"
            for extension, bucket_list in duplicate_extensions.items()
        )
        raise ConfigValidationError(
            f"Duplicate extensions detected: \n {duplicate_details}"
        )
