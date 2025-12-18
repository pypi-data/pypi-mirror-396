from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import ClassVar, Dict, Literal

from pydantic import Field, ConfigDict, field_validator, field_serializer
from typing_extensions import Annotated

from mixam_sdk.item_specification.enums.component_type import ComponentType
from mixam_sdk.item_specification.enums.flap_width import FlapWidth
from mixam_sdk.item_specification.interfaces.component_protocol import member_meta
from mixam_sdk.item_specification.models.custom_size import CustomSize
from mixam_sdk.item_specification.models.two_sided_component_support import (
    TwoSidedComponentSupport,
)
from mixam_sdk.utils.enum_json import enum_by_name_or_value, enum_dump_name


class DustJacketComponent(TwoSidedComponentSupport):

    FIELDS: ClassVar[Dict[str, str]] = {
        "flap_width": "j",
        "custom_flap_width": "m",
    }

    component_type: Literal[ComponentType.DUST_JACKET] = Field(
        default=ComponentType.DUST_JACKET,
        alias="componentType",
        validation_alias="componentType",
        frozen=True
    )

    flap_width: Annotated[FlapWidth, enum_by_name_or_value(FlapWidth), enum_dump_name] = Field(
        default=FlapWidth.AUTOMATIC,
        alias="flapWidth",
        description="Width of the dust-jacket flap.",
        json_schema_extra=member_meta(FIELDS["flap_width"]),
    )

    custom_flap_width: Decimal = Field(
        default_factory=lambda: Decimal("0").quantize(
            Decimal("0." + ("0" * CustomSize.CUSTOM_DIMENSION_SCALE)), rounding=ROUND_HALF_UP
        ),
        alias="customFlapWidth",
        description="Custom width of the dust-jacket flap if flap_width is set to CUSTOM.",
        json_schema_extra=member_meta(FIELDS["custom_flap_width"]),
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        frozen=False,
        strict=True,
        validate_assignment=True
    )

    @field_validator("custom_flap_width", mode="before")
    @classmethod
    def _coerce_custom_flap_width(cls, v):
        if v is None:
            return CustomSize._scale_decimal(Decimal("0"))
        return CustomSize._scale_decimal(v)

    def set_custom_flap_width(self, value: Decimal | int | float | str) -> None:
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        if CustomSize.CUSTOM_DIMENSION_SCALE == 0:
            value = value.to_integral_value(rounding=ROUND_HALF_UP)
        else:
            fmt = "0." + ("0" * CustomSize.CUSTOM_DIMENSION_SCALE)
            value = value.quantize(Decimal(fmt), rounding=ROUND_HALF_UP)
        self.custom_flap_width = value

    @field_serializer("custom_flap_width", when_used="json")
    def _serialize_custom_flap_width(self, v: Decimal):
        # Emit numbers (int for whole numbers, float otherwise) instead of strings like "0.00"
        try:
            if v == v.to_integral_value(rounding=ROUND_HALF_UP):
                return int(v)
            return float(v)
        except Exception:
            # Fallback to float conversion
            return float(v)