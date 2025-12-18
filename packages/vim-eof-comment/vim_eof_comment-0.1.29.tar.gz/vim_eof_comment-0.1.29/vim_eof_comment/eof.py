# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""Ensure EOF Vim comment in specific filetypes.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
from io import TextIOWrapper
from typing import Dict, List, NoReturn, Tuple

from colorama import Fore, Style
from colorama import init as color_init

from .args.parsing import arg_parser_init, indent_handler
from .comments import Comments
from .file import bootstrap_paths, get_last_line, modify_file, open_batch_paths
from .types.typeddict import (BatchPathDict, EOFCommentSearch, IndentHandler,
                              IOWrapperBool)
from .types.version import version_info
from .util import die, gen_indent_maps, verbose_print, version_print

_RED: int = Fore.LIGHTRED_EX
_GREEN: int = Fore.LIGHTGREEN_EX
_BRIGHT: int = Style.BRIGHT
_RESET: int = Style.RESET_ALL


def eof_comment_search(
        files: Dict[str, BatchPathDict],
        comments: Comments,
        newline: bool,
        verbose: bool
) -> Dict[str, EOFCommentSearch]:
    """Searches through opened files."""
    result = dict()
    comment_map = comments.generate()

    color_init()

    verbose_print(f"{_RESET}Analyzing files...\n", verbose=verbose)
    for path, file in files.items():
        file_obj: TextIOWrapper = file["file"]
        ext: str = file["ext"]

        wrapper = get_last_line(file_obj)
        last_line, has_nwl = wrapper["line"], wrapper["has_nwl"]

        verbose_print(f"{_RESET} - {path} ==> ", verbose=verbose, end="", sep="")
        if last_line != comment_map[ext]:
            verbose_print(f"{_BRIGHT}{_RED}CHANGED", verbose=verbose)
            result[path] = EOFCommentSearch(
                state=IOWrapperBool(file=open(path, "r"), has_nwl=has_nwl),
                lang=ext
            )
        else:
            verbose_print(f"{_BRIGHT}{_GREEN}OK", verbose=verbose)

    return result


def append_eof_comment(
        files: Dict[str, EOFCommentSearch],
        comments: Comments,
        newline: bool
) -> NoReturn:
    """Append EOF comment to files missing it."""
    comment_map = comments.generate()
    for path, file in files.items():
        has_nwl, file_obj, ext = file["state"]["has_nwl"], file["state"]["file"], file["lang"]

        txt = modify_file(file_obj, comment_map, ext, newline, has_nwl)
        file_obj = open(path, "w")

        file_obj.write(txt)
        file_obj.close()


def main() -> int:
    """Execute main workflow."""
    parser, namespace = arg_parser_init()

    dirs: Tuple[str] = tuple(namespace.directories)
    exts: Tuple[str] = tuple(namespace.exts.split(","))
    newline: bool = namespace.newline
    indent: List[IndentHandler] = indent_handler(namespace.indent)
    verbose: bool = namespace.verbose
    version: bool = namespace.version

    if version:
        version_print(str(version_info))

    indent = gen_indent_maps(indent.copy())

    if indent is None:
        comments = Comments()
    else:
        comments = Comments(indent)

    files = open_batch_paths(bootstrap_paths(dirs, exts))
    if len(files) == 0:
        die("No matching files found!", code=1)

    results = eof_comment_search(files, comments, newline, verbose)
    if len(results) > 0:
        append_eof_comment(results, comments, newline)

    return 0

# vim: set ts=4 sts=4 sw=4 et ai si sta:
