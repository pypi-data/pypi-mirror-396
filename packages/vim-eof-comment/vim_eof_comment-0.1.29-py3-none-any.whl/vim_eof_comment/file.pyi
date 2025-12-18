from io import TextIOWrapper

from .types.typeddict import BatchPairDict as BatchPairDict
from .types.typeddict import BatchPathDict as BatchPathDict
from .types.typeddict import LineBool as LineBool
from .util import die as die
from .util import error as error

def bootstrap_paths(paths: tuple[str], exts: tuple[str]) -> list[BatchPairDict]:
    """Bootstraps all the matching paths in current dir and below."""
def open_batch_paths(paths: list[BatchPairDict]) -> dict[str, BatchPathDict]:
    """Return a list of TextIO objects given file path strings."""
def modify_file(file: TextIOWrapper, comments: dict[str, str], ext: str, newline: bool, has_nwl: bool) -> str:
    """Modifies a file containing a bad EOF comment."""
def get_last_line(file: TextIOWrapper) -> LineBool:
    """Returns the last line of a file."""

# vim: set ts=4 sts=4 sw=4 et ai si sta:
