from typing import Iterator, NoReturn

from .types.typeddict import IndentMap as IndentMap

_formats: dict[str, str]
_DEFAULT: dict[str, IndentMap]

class EOFCommentsError(Exception):
    """EOF Comments error type."""

class Comments:
    """Vim EOF comments class."""
    formats: dict[str, str]
    langs: dict[str, IndentMap]
    __DEFAULT: dict[str, IndentMap]
    def __init__(self, mappings: dict[str, IndentMap] | None = None) -> None:
        """Creates a new Vim EOF comment object."""
    def __iter__(self) -> Iterator[str]:
        """Iterate through comment langs."""
    def __is_available(self, lang: str) -> bool:
        """Checks if a given lang is available within the class."""
    def __fill_langs(self) -> NoReturn:
        """Fill languages dict."""
    def generate(self) -> dict[str, str]:
        """Generate the comments list."""

# vim: set ts=4 sts=4 sw=4 et ai si sta:
