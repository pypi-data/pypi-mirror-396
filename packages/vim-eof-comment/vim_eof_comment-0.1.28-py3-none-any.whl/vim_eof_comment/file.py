# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""File management utilities.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
from io import TextIOWrapper
from os import walk
from os.path import isdir, join
from typing import Dict, List, Tuple

from .types.typeddict import BatchPairDict, BatchPathDict, LineBool
from .util import die, error


def bootstrap_paths(paths: Tuple[str], exts: Tuple[str]) -> List[BatchPairDict]:
    """Bootstraps all the matching paths in current dir and below."""
    result = list()
    for path in paths:
        if not isdir(path):
            continue

        file: str
        for root, dirs, files in walk(path):
            for file in files:
                for ext in exts:
                    if not file.endswith(ext):
                        continue

                    result.append(BatchPairDict(fpath=join(root, file), ext=ext))

    return result


def open_batch_paths(paths: List[BatchPairDict]) -> Dict[str, BatchPathDict]:
    """Return a list of TextIO objects given file path strings."""
    result = dict()
    for path in paths:
        fpath, ext = path["fpath"], path["ext"]
        try:
            result[fpath] = {"file": open(fpath, "r"), "ext": ext}
        except KeyboardInterrupt:
            die("\nProgram interrupted!", code=1)  # Kills the program
        except FileNotFoundError:
            error(f"File `{fpath}` is not available!")
        except Exception:
            error(f"Something went wrong while trying to open `{fpath}`!")

    return result


def modify_file(
        file: TextIOWrapper,
        comments: Dict[str, str],
        ext: str,
        newline: bool,
        has_nwl: bool
) -> str:
    """Modifies a file containing a bad EOF comment."""
    data: List[str] = file.read().split("\n")
    file.close()

    data_len = len(data)
    comment = comments[ext]
    if data_len == 0:
        data = [comment, ""]
    elif data_len == 1:
        data.insert(0, comment)
    elif data_len >= 2:
        data.insert(-1, comment)

    if newline and not has_nwl:
        data.insert(-2, "")  # Newline

    return "\n".join(data)


def get_last_line(file: TextIOWrapper) -> LineBool:
    """Returns the last line of a file."""
    data: List[str] = file.read().split("\n")
    has_newline = False
    line = ""
    if len(data) == 1:
        line = data[0]
    elif len(data) >= 2:
        if len(data) >= 3:
            has_newline = data[-3] == ""

        line: str = data[-2]

    file.close()

    return LineBool(line=line, has_nwl=has_newline)

# vim: set ts=4 sts=4 sw=4 et ai si sta:
