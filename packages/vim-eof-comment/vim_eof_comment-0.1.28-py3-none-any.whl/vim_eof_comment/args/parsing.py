# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""Argparse utilities.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
from argparse import ArgumentError, ArgumentParser, Namespace
from typing import List, Tuple

from ..types.typeddict import IndentHandler, ParserSpec
from ..util import die


def bootstrap_args(
        parser: ArgumentParser,
        specs: Tuple[ParserSpec]
) -> Namespace:
    """Bootstraps the program arguments."""
    for spec in specs:
        opts, kwargs = spec["opts"], spec["kwargs"]
        parser.add_argument(*opts, **kwargs)

    try:
        namespace: Namespace = parser.parse_args()
    except ArgumentError:
        die(code=1, func=parser.print_usage)

    return namespace


def arg_parser_init() -> Tuple[ArgumentParser, Namespace]:
    """Generates the argparse namespace."""
    parser = ArgumentParser(
        prog="ensure_eof_comment.py",
        description="Checks for Vim EOF comments in all matching files in specific directories",
        exit_on_error=False
    )
    spec: Tuple[ParserSpec] = (
        {
            "opts": ["directories"],
            "kwargs": {
                "nargs": "+",
                "help": "The target directories to be checked",
                "metavar": "/path/to/directory",
            },
        },
        {
            "opts": ["-V", "--version"],
            "kwargs": {
                "required": False,
                "action": "store_true",
                "help": "Show version",
                "dest": "version",
            }
        },
        {
            "opts": ["-e", "--extensions"],
            "kwargs": {
                "required": True,
                "metavar": "EXT1[,EXT2[,EXT3[,...]]]",
                "help": "A comma-separated list of file extensions (e.g. \"lua,c,cpp,cc,c++\")",
                "dest": "exts",
            }
        },
        {
            "opts": ["-n", "--newline"],
            "kwargs": {
                "required": False,
                "action": "store_true",
                "help": "Add newline before EOF comment",
                "dest": "newline",
            }
        },
        {
            "opts": ["-v", "--verbose"],
            "kwargs": {
                "required": False,
                "action": "store_true",
                "help": "Enable verbose mode",
                "dest": "verbose",
            }
        },
        {
            "opts": ["-i"],
            "kwargs": {
                "required": False,
                "metavar": "EXT1:INDENT1[:<Y|N>][,...]",
                "help": """
                A comma-separated list of per-extension mappings
                (indent level and, optionally, a Y/N value to indicate if tabs are expanded).
                For example: "lua:4,py:4:Y,md:2:N"
                """,
                "default": "",
                "dest": "indent",
            },
        },
    )

    return parser, bootstrap_args(parser, spec)


def indent_handler(indent: str) -> List[IndentHandler]:
    """Parse indent levels defined by the user."""
    if indent == "":
        return list()

    indents: List[str] = indent.split(",")
    maps: List[IndentHandler] = list()
    for ind in indents:
        inds: List[str] = ind.split(":")
        if len(inds) <= 1:
            continue

        ext, ind_level, et = inds[0], int(inds[1]), True
        if len(inds) >= 3 and inds[2].upper() in ("Y", "N"):
            et = False if inds[2].upper() == "N" else True

        maps.append(IndentHandler(ext=ext, level=ind_level, expandtab=et))

    return maps

# vim: set ts=4 sts=4 sw=4 et ai si sta:
