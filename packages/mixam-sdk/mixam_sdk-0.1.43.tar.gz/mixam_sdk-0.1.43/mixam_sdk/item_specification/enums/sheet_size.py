from __future__ import annotations

from enum import Enum

from mixam_sdk.item_specification.enums.standard_size import StandardSize
from mixam_sdk.item_specification.models.value_based import ValueBased


class SheetSize(ValueBased, Enum):
    NOT_APPLICABLE = (0, 0, StandardSize.NONE)
    SRA0 = (1, 0, StandardSize.SRA0)
    SRA1 = (2, 1, StandardSize.SRA1)
    SRA2 = (3, 2, StandardSize.SRA2)
    SRA3 = (4, 3, StandardSize.SRA3)
    SRA4 = (5, 4, StandardSize.SRA4)

    def __init__(self, value_id: int, format: int, standard_size: StandardSize):
        self._value_ = value_id
        self._format = format
        self._standard_size = standard_size

    def get_value(self) -> int:
        return int(self.value)

    def get_format(self) -> int:
        return self._format

    def get_standard_size(self) -> StandardSize:
        return self._standard_size
