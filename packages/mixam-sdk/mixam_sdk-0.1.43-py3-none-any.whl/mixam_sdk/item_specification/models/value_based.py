from __future__ import annotations

from enum import Enum
from typing import Type, TypeVar, cast
from functools import cache

DEPRECATED_MEMBERS = [
    "PERFECT",
    "LOOP",
    "COLORPLAN_SORBET_YELLOW",
    "ENVELOPES",
    "WALL_CALENDARS",
    "DESK_CALENDARS",
    "IN_8_5_X_3_5",
    "IN_8_5_X_5_5",
]


class ValueBased:
    def get_value(self) -> int:
        raise NotImplementedError

    @staticmethod
    def for_value(value: int, enum_cls: Type[T]) -> T:
        if not issubclass(enum_cls, Enum):
            raise TypeError(f"{enum_cls} is not an Enum")
        for constant in enum_cls:
            gv = getattr(constant, "get_value", None)
            current = gv() if callable(gv) else constant.value
            if current == value:
                return constant
        raise ValueError(f"Unrecognized value: {value} for {enum_cls.__name__}")

    @classmethod
    @cache
    def text_based(cls: Type[T]) -> Type[Enum]:
        if not issubclass(cls, Enum):
            raise TypeError(f"{cls.__name__} is not an Enum")
        return Enum(
            f"{cls.__name__}TextBased",
            {
                member.name: member.name
                for member in cls
                if member.name not in DEPRECATED_MEMBERS
            },
        )

    @classmethod
    @cache
    def from_text_based(cls: Type[T], text_member: Enum) -> T:
        """
        Given a text-based enum member, return the corresponding value-based member.
        """
        if not isinstance(text_member, Enum):
            raise TypeError(f"{text_member} is not an Enum member")

        try:
            return cls[text_member.name]
        except KeyError:
            raise ValueError(f"{text_member.name} not found in {cls.__name__}")

    @cache
    def to_text_based(self) -> T:
        return type(self).text_based()[cast(Enum, self).name]


T = TypeVar("T", bound=Enum)


def for_value(value: int, enum_cls: Type[T]) -> T:
    if not issubclass(enum_cls, Enum):
        raise TypeError(f"{enum_cls} is not an Enum")

    for constant in enum_cls:
        gv = getattr(constant, "get_value", None)
        current = gv() if callable(gv) else constant.value
        if current == value:
            return constant
    raise ValueError(f"Unrecognized value: {value} for {enum_cls.__name__}")
