"""Tests ensuring typing stays in sync with enums"""
from superautosim.typing import SingleFilterDict, MultiFilterDict, SingleFilterValue
from superautosim.targets import FilterType

import typing


def test_single_filter_dict():
    literals = set(typing.get_args(SingleFilterValue))
    enums = set(type.name for type in FilterType)
    assert literals == enums
