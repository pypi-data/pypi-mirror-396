from io import TextIOWrapper
from typing import Any, TypedDict

class ParserSpec(TypedDict):
    """A TypeDict container."""
    opts: tuple[str]
    kwargs: dict[str, Any]

class CommentMap(TypedDict):
    """A TypeDict container."""
    level: int

class IndentMap(TypedDict):
    """A TypeDict container."""
    level: int
    expandtab: bool

class IndentHandler(TypedDict):
    """A TypeDict container."""
    ext: str
    level: str
    expandtab: bool

class IOWrapperBool(TypedDict):
    """A TypeDict container."""
    file: TextIOWrapper
    has_nwl: bool

class LineBool(TypedDict):
    """A TypeDict container."""
    line: str
    has_nwl: bool

class BatchPathDict(TypedDict):
    """A TypeDict container."""
    file: TextIOWrapper
    ext: str

class BatchPairDict(TypedDict):
    """A TypeDict container."""
    fpath: str
    ext: str

class EOFCommentSearch(TypedDict):
    """A TypeDict container."""
    state: IOWrapperBool
    lang: str

# vim: set ts=4 sts=4 sw=4 et ai si sta:
