from __future__ import annotations

from typing import Protocol

from mixam_sdk.item_specification.enums.standard_size import StandardSize
from mixam_sdk.item_specification.enums.substrate_design import SubstrateDesign
from mixam_sdk.item_specification.interfaces.component_protocol import TwoSidedComponent as ITwoSidedComponent
from mixam_sdk.item_specification.models.component_support import ComponentSupport
from mixam_sdk.item_specification.models.item_specification import ItemSpecification
from mixam_sdk.metadata.product.models.product_metadata import ProductMetadata
from mixam_sdk.metadata.product.services.validation_result import ValidationResult


class ComponentValidator(Protocol):
    def validate(self, product_metadata: ProductMetadata, item_specification: ItemSpecification, component: ComponentSupport, result: ValidationResult, base_path: str) -> None: ...


class DefaultComponentValidator:
    """
    Applies standard validations common to all components. More specific validators
    can subclass this and extend/override validate.
    """

    def validate(self, product_metadata: ProductMetadata, item_specification: ItemSpecification, component: ComponentSupport, result: ValidationResult, base_path: str) -> None:
        try:
            allowed_formats = {s.format for s in product_metadata.standard_sizes}
            if component.format not in allowed_formats:
                result.add_error(
                    path=f"{base_path}.format",
                    message=f"Format '{component.format}' not available for this product.",
                    code="size.format.unavailable",
                    allowed=sorted(list(allowed_formats)),
                )
        except Exception:
            pass

        try:
            ss = component.standard_size
            if not isinstance(ss, StandardSize):
                result.add_error(
                    path=f"{base_path}.standardSize",
                    message=f"Invalid standardSize value '{ss}'.",
                    code="size.standard.invalid",
                )
            else:
                if ss is not StandardSize.NONE:
                    try:
                        expected_fmt = ss.get_format()
                        if component.format != expected_fmt:
                            result.add_error(
                                path=f"{base_path}.format",
                                message=(
                                    f"Format '{component.format}' does not match required format for standardSize '{ss.name}'."
                                ),
                                code="size.standard.format.mismatch",
                                expected=expected_fmt,
                                standardSize=ss.name,
                            )
                    except Exception:
                        pass

                    allowed_standard_sizes = {m.standard_size for m in product_metadata.standard_sizes}
                    if allowed_standard_sizes and ss not in allowed_standard_sizes:
                        result.add_error(
                            path=f"{base_path}.standardSize",
                            message=f"Standard size '{ss.name}' not available for this product.",
                            code="size.standard.unavailable",
                            allowed=sorted([s.name for s in allowed_standard_sizes]),
                        )
        except Exception:
            pass

        try:
            design = component.substrate.design
            if isinstance(design, SubstrateDesign) and design is not SubstrateDesign.NONE:
                allowed_designs = {sd.substrate_design.name for sd in product_metadata.substrate_designs}
                if allowed_designs and design.name not in allowed_designs:
                    result.add_error(
                        path=f"{base_path}.substrate.design",
                        message=f"Substrate design '{design.name}' not available for this product.",
                        code="substrate.design.unavailable",
                        allowed=sorted(list(allowed_designs)),
                    )
        except Exception:
            pass


__all__ = [
    "ComponentValidator",
    "DefaultComponentValidator",
]
