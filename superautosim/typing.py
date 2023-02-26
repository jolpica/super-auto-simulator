from __future__ import annotations
from typing import TypedDict, Literal, Union


SingleFilterValue = Literal[
    "NONE", "SELF", "NOT_SELF", "FRIENDLY", "ENEMY", "AHEAD", "BEHIND", "ADJACENT"
]


class SingleFilterDict(TypedDict, total=True):
    filter: SingleFilterValue


class MultiFilterDict(TypedDict, total=True):
    op: Literal["ANY", "ALL"]
    filters: list[FilterDict]


FilterDict = Union[MultiFilterDict, SingleFilterDict]
