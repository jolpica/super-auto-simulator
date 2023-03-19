"""Tests ensuring typing stays in sync with enums"""
from superautosim.typing import (
    SingleFilterDict,
    MultiFilterDict,
    SingleFilterValue,
    MultiFilterValue,
)
from superautosim.targets import FilterType, MultiFilterType

import typing


def test_single_filter_dict():
    literals = set(typing.get_args(SingleFilterValue))
    enums = set(type.name for type in FilterType)
    assert literals == enums


def test_mult_filter_dict():
    literals = set(typing.get_args(MultiFilterValue))
    enums = set(type.name for type in MultiFilterType)
    assert literals == enums
