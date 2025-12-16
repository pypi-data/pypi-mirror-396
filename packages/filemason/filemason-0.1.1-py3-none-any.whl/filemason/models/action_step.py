"""Domain model for representing a singular action step to be taken"""

from enum import Enum
from pathlib import Path
from pydantic import BaseModel, ConfigDict


class Action(str, Enum):
    """Enumeration of possible actions an ActionStep can perform."""

    move = "MOVE"
    mkdir = "MKDIR"


class ActionStep(BaseModel):
    """
    Domain model for a singular action step to be taken by the application.

    Attributes:
        id: The hashed ID of the FileItem
        action: The type of action to perform (move, mkdir, or rename).
        source: The source path relevant to the operation. May be None for mkdir.
        destination: The destination path relevant to the operation.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_id: str | None = None
    action: Action
    source: Path | None = None
    destination: Path
