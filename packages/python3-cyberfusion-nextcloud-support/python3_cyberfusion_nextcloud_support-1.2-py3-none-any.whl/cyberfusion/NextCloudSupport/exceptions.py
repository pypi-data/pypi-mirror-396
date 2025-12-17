"""Exceptions."""

from dataclasses import dataclass
from typing import List


class DirectoryNotEmptyError(Exception):
    """Directory is not empty."""

    pass


class AppNotInstalledError(Exception):
    """App should be installed, but is not."""

    pass


@dataclass
class CommandFailedError(Exception):
    """Command failed."""

    command: List[str]
    return_code: int
    stdout: str
    stderr: str

    @property
    def streams(self) -> str:
        """Combine output streams."""
        return f"Stdout:\n\n{self.stdout}\n\nStderr:\n\n{self.stderr}"
