from typing import Callable, NoReturn, TextIO

from .types.typeddict import IndentHandler as IndentHandler
from .types.typeddict import IndentMap as IndentMap

def error(*msg, end: str = '\n', sep: str = ' ', flush: bool = False) -> NoReturn:
    """Prints to stderr."""
def die(*msg, code: int = 0, end: str = '\n', sep: str = ' ', flush: bool = False, func: Callable[[TextIO], None] | None = None) -> NoReturn:
    """Kill program execution."""
def verbose_print(*msg, verbose: bool | None = None, **kwargs) -> NoReturn:
    """Only print if verbose mode is activated."""
def version_print(version: str) -> NoReturn:
    """Print project version, then exit."""
def gen_indent_maps(maps: list[IndentHandler]) -> dict[str, IndentMap] | None:
    """Generate a dictionary from the custom indent maps."""

# vim: set ts=4 sts=4 sw=4 et ai si sta:
