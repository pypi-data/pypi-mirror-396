from __future__ import annotations

from enum import Enum

from mixam_sdk.item_specification.models.value_based import ValueBased


class Shape(ValueBased, Enum):
    NONE = 0
    SQUARE = 1
    RECTANGLE = 2
    CIRCLE = 3
    OVAL = 4
    HEART = 5
    GIFT_BOX = 6
    STAR = 7
    TREE = 8

    def get_value(self) -> int:
        return int(self.value)
