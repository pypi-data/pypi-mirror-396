from _typeshed import Incomplete

class _VersionInfo:
    """
    A sys-inspired version_info object type.

    Attributes
    ----------
        major: int
        minor: int
        patch: int
    """
    major: int
    minor: int
    patch: int
    def __init__(self, major: int, minor: int, patch: int) -> None:
        """Initialize _VersionInfo object."""
    def __str__(self) -> str:
        """Representate this object as a string."""

version_info: Incomplete
# vim: set ts=4 sts=4 sw=4 et ai si sta:
