from typing import Self
from mixam_sdk.item_specification.enums.standard_size import StandardSize
from enum import Enum
from pydantic import BaseModel

StandardSizeTextBased = StandardSize.text_based()

SizeTextBased = Enum(
    "SizeTextBased",
    {
        **{s.name: s.value for s in StandardSizeTextBased if s.name != "NONE"},
        **{f"A{s}": f"A{s}" for s in range(0, 9)},
    },
)


class FormatAndStandardSize(BaseModel):
    format: int
    standard_size: StandardSize

    @classmethod
    def from_size_text_based(cls, size: SizeTextBased) -> Self:  # pyright: ignore[reportInvalidTypeForm]
        if size.name not in StandardSizeTextBased._member_names_:
            return cls(format=str(size.value[1]), standard_size=StandardSize.NONE)

        return cls(
            format=StandardSize[size.name].get_format(),
            standard_size=StandardSize[size.name],
        )
