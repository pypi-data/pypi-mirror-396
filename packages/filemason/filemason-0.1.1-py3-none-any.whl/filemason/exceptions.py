class ConfigError(Exception):
    """Base class for configuration-related errors."""

    pass


class ConfigFileError(ConfigError):
    """Errors related to reading or accessing the config file."""

    pass


class ConfigParseError(ConfigError):
    """Errors related to parsing the TOML contents."""

    pass


class ConfigValidationError(ConfigError):
    """Errors related to the logical structure or contents of the config."""

    pass


class ExecutorError(Exception):
    """Base class for Executor Errors"""

    pass


class MoveError(ExecutorError):
    """Errors related to files being moved by the executor service."""

    pass
