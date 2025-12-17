"""User."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from cyberfusion.NextCloudSupport.instance import Instance


class User:
    """Represents user."""

    def __init__(self, instance: "Instance", id_: str, name: str) -> None:
        """Set attributes."""
        self.instance = instance
        self.id = id_
        self.name = name
