# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""Custom vim-eof-comment versioning objects.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""


class _VersionInfo():
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

    def __init__(self, major: int, minor: int, patch: int):
        """Initialize _VersionInfo object."""
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self) -> str:
        """Representate this object as a string."""
        return f"{self.major}.{self.minor}.{self.patch}"


version_info = _VersionInfo(0, 1, 29)
# vim: set ts=4 sts=4 sw=4 et ai si sta:
