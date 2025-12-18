from typing import Union, get_args
from .binding_colour import BindingColour
from .binding_edge import BindingEdge
from .binding_loops import BindingLoops
from .binding_type import BindingType
from .border_type import BorderType
from .colours import Colours
from .component_type import ComponentType
from .cover_area import CoverArea
from .end_paper_colour import EndPaperColour
from .flap_width import FlapWidth
from .foiling_colour import FoilingColour
from .frame_depth import FrameDepth
from .head_and_tail_bands import HeadAndTailBands
from .lamination import Lamination
from .orientation import Orientation
from .pre_drilled_holes import PreDrilledHoles
from .product import Product
from .ribbon_colour import RibbonColour
from .sample_pack_type import SamplePackType
from .shape import Shape
from .sheet_size import SheetSize
from .simple_fold import SimpleFold
from .standard_size import StandardSize
from .substrate_colour import SubstrateColour
from .substrate_design import SubstrateDesign
from .substrate_group import SubstrateGroup
from .substrate_type import SubstrateType
from .substrate_weights import SubstrateWeights
from .unit_format import UnitFormat

ValueBasedSpecificationOptionEnum = (
    BindingColour
    | BindingEdge
    | BindingLoops
    | BindingType
    | BorderType
    | Colours
    | CoverArea
    | EndPaperColour
    | FlapWidth
    | FrameDepth
    | HeadAndTailBands
    | Lamination
    | Orientation
    | PreDrilledHoles
    | Product
    | RibbonColour
    | SamplePackType
    | Shape
    | SheetSize
    | SimpleFold
    | StandardSize
    | SubstrateColour
    | SubstrateDesign
    | SubstrateGroup
    | SubstrateType
    | UnitFormat
)

TextBasedSpecificationOptionEnum = Union[
    *(t.text_based() for t in get_args(ValueBasedSpecificationOptionEnum))
]


__all__ = [
    "BindingColour",
    "BindingEdge",
    "BindingLoops",
    "BindingType",
    "BorderType",
    "Colours",
    "ComponentType",
    "CoverArea",
    "EndPaperColour",
    "FlapWidth",
    "FoilingColour",
    "FrameDepth",
    "HeadAndTailBands",
    "Lamination",
    "Orientation",
    "PreDrilledHoles",
    "Product",
    "RibbonColour",
    "SamplePackType",
    "Shape",
    "SheetSize",
    "SimpleFold",
    "StandardSize",
    "SubstrateColour",
    "SubstrateDesign",
    "SubstrateGroup",
    "SubstrateType",
    "SubstrateWeights",
    "UnitFormat",
    "ValueBasedSpecificationOptionEnum",
]
