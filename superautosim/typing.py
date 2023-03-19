from __future__ import annotations
from typing import TypedDict, Literal, Union


SingleFilterValue = Literal[
    "NONE", "SELF", "NOT_SELF", "FRIENDLY", "ENEMY", "AHEAD", "BEHIND", "ADJACENT"
]


class SingleFilterDict(TypedDict, total=True):
    filter: SingleFilterValue


MultiFilterValue = Literal["ANY", "ALL"]


class MultiFilterDict(TypedDict, total=True):
    op: MultiFilterValue
    filters: list[FilterDict]


FilterDict = Union[MultiFilterDict, SingleFilterDict]
