from argparse import ArgumentParser, Namespace

from ..types.typeddict import IndentHandler as IndentHandler
from ..types.typeddict import ParserSpec as ParserSpec
from ..util import die as die

def bootstrap_args(parser: ArgumentParser, specs: tuple[ParserSpec]) -> Namespace:
    """Bootstraps the program arguments."""
def arg_parser_init() -> tuple[ArgumentParser, Namespace]:
    """Generates the argparse namespace."""
def indent_handler(indent: str) -> list[IndentHandler]:
    """Parse indent levels defined by the user."""

# vim: set ts=4 sts=4 sw=4 et ai si sta:
