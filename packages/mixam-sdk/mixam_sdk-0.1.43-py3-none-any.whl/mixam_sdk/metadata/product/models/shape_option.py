from __future__ import annotations

from typing import Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict

from mixam_sdk.item_specification.enums.shape import Shape
from mixam_sdk.item_specification.enums.sheet_size import SheetSize
from mixam_sdk.item_specification.enums.orientation import Orientation
from mixam_sdk.utils.enum_json import enum_by_name_or_value, enum_dump_name
from mixam_sdk.metadata.product.enums.trilean import Trilean


class ShapeOption(BaseModel):
    """
    Metadata model mirroring ShapeOption from Java services.
    Represents a single shape configuration option for a given size, including
    optional sheet information and rounded corners availability.
    """

    shape: Annotated[Shape, enum_by_name_or_value(Shape), enum_dump_name] = Field(
        alias="shape",
    )

    label: str = Field(
        alias="label",
    )

    value: int = Field(
        alias="value",
    )

    orientation: Annotated[
        Orientation, enum_by_name_or_value(Orientation), enum_dump_name
    ] = Field(
        alias="orientation",
    )

    amount_per_sheet: int = Field(
        default=1,
        alias="amountPerSheet",
    )

    sheet_size: Annotated[
        SheetSize, enum_by_name_or_value(SheetSize), enum_dump_name
    ] = Field(
        default=SheetSize.NOT_APPLICABLE,
        alias="sheetSize",
    )

    # Use a forward reference to avoid circular import issues with StandardSizeMetadata
    sheet_size_metadata: Optional["StandardSizeMetadata"] = Field(
        default=None,
        alias="sheetSizeMetadata",
    )

    rounded_corners: Annotated[
        Trilean, enum_by_name_or_value(Trilean), enum_dump_name
    ] = Field(
        default=Trilean.UNAVAILABLE,
        alias="roundedCorners",
    )

    santa_default: bool = Field(
        default=False,
        alias="santaDefault",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        frozen=True,
        strict=True,
        validate_assignment=True,
    )


__all__ = ["ShapeOption"]
