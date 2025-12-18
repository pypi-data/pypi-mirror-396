from typing import NoReturn

from .args.parsing import arg_parser_init as arg_parser_init
from .args.parsing import indent_handler as indent_handler
from .comments import Comments as Comments
from .file import bootstrap_paths as bootstrap_paths
from .file import get_last_line as get_last_line
from .file import modify_file as modify_file
from .file import open_batch_paths as open_batch_paths
from .types.typeddict import BatchPathDict as BatchPathDict
from .types.typeddict import EOFCommentSearch as EOFCommentSearch
from .types.typeddict import IndentHandler as IndentHandler
from .types.typeddict import IOWrapperBool as IOWrapperBool
from .types.version import version_info as version_info
from .util import die as die
from .util import gen_indent_maps as gen_indent_maps
from .util import verbose_print as verbose_print
from .util import version_print as version_print

_RED: int
_GREEN: int
_BRIGHT: int
_RESET: int

def eof_comment_search(files: dict[str, BatchPathDict], comments: Comments, newline: bool, verbose: bool) -> dict[str, EOFCommentSearch]:
    """Searches through opened files."""
def append_eof_comment(files: dict[str, EOFCommentSearch], comments: Comments, newline: bool) -> NoReturn:
    """Append EOF comment to files missing it."""
def main() -> int:
    """Execute main workflow."""

# vim: set ts=4 sts=4 sw=4 et ai si sta:
