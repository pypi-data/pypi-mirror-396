"""
ODS Models - Canvas Globals
Global canvas configuration including presets, guides, and grids.
Python equivalent of @optikka/ods-models/canvasGlobals
"""

from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel


class CanvasGuideKind(str, Enum):
    """Canvas guide kind"""
    BOX = "box"
    POINT = "point"


class CanvasGridKind(str, Enum):
    """Canvas grid type"""
    SIMPLE = "simple"
    BENTO = "bento"


class BentoAxis(str, Enum):
    """Bento grid axis"""
    ROW = "row"
    COL = "col"


class FlexPreset(BaseModel):
    """Canvas aspect ratio preset"""
    canvas_width: float
    canvas_height: float
    label: str
    id: str


class CanvasGuides(BaseModel):
    """Canvas guide definition"""
    id: str
    name: str
    slot_key: str
    cases: Optional[Dict[str, Dict[str, float]]] = None
    x1: float
    y1: float
    x2: float
    y2: float
    layer_id: Optional[str] = None
    is_point: Optional[bool] = None
    kind: CanvasGuideKind
    dir: Optional[Dict[str, float]] = None


class CanvasGridBase(BaseModel):
    """Base class for canvas grids"""
    kind: CanvasGridKind
    id: str


class CanvasSimpleGridDef(CanvasGridBase):
    """Simple grid definition with columns and rows"""
    kind: CanvasGridKind = CanvasGridKind.SIMPLE
    columns: int
    rows: Optional[int] = None
    marginX: Optional[float] = None
    marginY: Optional[float] = None
    gutterX: Optional[float] = None
    gutterY: Optional[float] = None


class CanvasBentoNode(BaseModel):
    """Bento grid node"""
    id: str
    type: BentoAxis
    size: float
    children: Optional[List["CanvasBentoNode"]] = None


class CanvasBentoGridDef(CanvasGridBase):
    """Bento grid definition with nested nodes"""
    kind: CanvasGridKind = CanvasGridKind.BENTO
    root: List[CanvasBentoNode]


# Union type for grid definitions
CanvasGridDef = Union[CanvasSimpleGridDef, CanvasBentoGridDef]


class CanvasGlobals(BaseModel):
    """
    Global canvas configuration.
    Contains flex presets, guides, and optional grid definitions.
    """
    flex_presets: Dict[str, FlexPreset]
    canvas_guides: List[CanvasGuides]
    canvas_grids: Optional[List[CanvasGridDef]] = None


# Update forward references for recursive model
CanvasBentoNode.model_rebuild()
