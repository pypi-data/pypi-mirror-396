# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""EOF comments checker utilities.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
from sys import exit as Exit
from sys import stderr as STDERR
from sys import stdout as STDOUT
from typing import Callable, Dict, List, NoReturn, TextIO

from .types.typeddict import IndentHandler, IndentMap


def error(*msg, end: str = "\n", sep: str = " ", flush: bool = False) -> NoReturn:
    """Prints to stderr."""
    try:
        end = str(end)
    except KeyboardInterrupt:
        Exit(1)
    except Exception:
        end = "\n"

    try:
        sep = str(sep)
    except KeyboardInterrupt:
        Exit(1)
    except Exception:
        sep = " "

    try:
        flush = bool(flush)
    except KeyboardInterrupt:
        Exit(1)
    except Exception:
        flush = False

    print(*msg, end=end, sep=sep, flush=flush, file=STDERR)


def die(
        *msg,
        code: int = 0,
        end: str = "\n",
        sep: str = " ",
        flush: bool = False,
        func: Callable[[TextIO], None] | None = None,
) -> NoReturn:
    """Kill program execution."""
    try:
        code = int(code)
    except Exception:
        code = 1

    try:
        end = str(end)
    except Exception:
        end = "\n"
        code = 1

    try:
        sep = str(sep)
    except Exception:
        sep = " "
        code = 1

    try:
        flush = bool(flush)
    except Exception:
        flush = False
        code = 1

    if func is not None and callable(func):
        func(STDERR if code != 0 else STDOUT)

    if msg and len(msg) > 0:
        if code == 0:
            print(*msg, end=end, sep=sep, flush=flush)
        else:
            error(*msg, end=end, sep=sep, flush=flush)

    Exit(code)


def verbose_print(*msg, verbose: bool | None = None, **kwargs) -> NoReturn:
    """Only print if verbose mode is activated."""
    end: str = kwargs.get("end", "\n")
    sep: str = kwargs.get("sep", " ")
    flush: bool = kwargs.get("flush", False)

    if verbose is None or not verbose:
        return

    print(*msg, end=end, sep=sep, flush=flush)


def version_print(version: str) -> NoReturn:
    """Print project version, then exit."""
    die(f"vim-eof-comment: v{version}", code=0)


def gen_indent_maps(
        maps: List[IndentHandler]
) -> Dict[str, IndentMap] | None:
    """Generate a dictionary from the custom indent maps."""
    if len(maps) == 0:
        return None

    map_d: Dict[str, IndentMap] = dict()
    for mapping in maps:
        mapping_len = len(mapping)
        if mapping_len <= 1:
            raise ValueError(f"One of the custom mappings is not formatted properly! (`{mapping}`)")

        ext, level = mapping["ext"], mapping["level"]
        if ext in map_d.keys():
            continue

        mapping_len = mapping_len if mapping_len <= 3 else 3
        map_d[ext] = {
            "level": level,
            "expandtab": True if mapping_len == 2 else mapping["expandtab"],
        }

    return map_d

# vim: set ts=4 sts=4 sw=4 et ai si sta:
