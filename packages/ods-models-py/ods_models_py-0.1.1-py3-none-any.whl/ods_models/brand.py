"""
ODS Models - Brand
Brand-related models including colors, color palettes, and brand rules.
Python equivalent of brand models from design-data-microservices.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from ods_types.enums import ColorType, BrandRuleType, BrandRuleTarget, DataType
from ods_models.template_input import Logo


class RGB(BaseModel):
    """
    RGB color values.
    """
    r: int
    g: int
    b: int


class HSL(BaseModel):
    """
    HSL color values.
    """
    h: float
    s: float
    l: float


class HSV(BaseModel):
    """
    HSV color values.
    """
    h: float
    s: float
    v: float


class CMYK(BaseModel):
    """
    CMYK color values.
    """
    c: float
    m: float
    y: float
    k: float


class Color(BaseModel):
    """
    Color definition with multiple color space representations.
    """
    type: ColorType
    hex: str
    rgb: RGB
    hsl: HSL
    hsv: HSV
    cmyk: CMYK
    pantone: str
    description: str


class ColorPalette(BaseModel):
    """
    Color palette with named colors indexed by color number.
    """
    name: str
    description: str
    whenToUsePrompt: str
    colors: Dict[int, Color]  # key is the color index 1 for primary, 2 for secondary, etc.


class BrandRule(BaseModel):
    """
    Brand rule definition.
    """
    type: BrandRuleType
    target: BrandRuleTarget
    description: str
    value: str
    priority: int
    enabled: bool


class ImageQueryHint(BaseModel):
    """
    Image query hint.
    """
    name: str
    description: str
    should_pull_from_batch_ids: bool


class EntityAttributeSpec(BaseModel):
    """
    Entity attribute specification.
    """
    name: str
    description: str
    type: DataType
    required: bool
    default_value: Any


class BrandRegistry(BaseModel):
    """
    Brand Registry - Runtime data interface.
    """
    id: Optional[str] = None  # Optional: frontend uses 'id', backend uses '_id' from Mongoose
    name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    account_ids: List[str] = Field(default_factory=list)
    is_universal: bool = False
    studio_ids: List[str] = Field(default_factory=list)
    industries: List[str] = Field(default_factory=list)
    entity_attributes_specs: Dict[str, EntityAttributeSpec] = Field(default_factory=dict)  # entity attributes for the brand (e.g. industry, team name, etc.)
    required_images: Dict[str, ImageQueryHint] = Field(default_factory=dict)  # image to parse for the brand (team star, team players)


class BrandRegistryWithoutId(BaseModel):
    """
    Brand registry for insert.
    """
    name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    account_ids: List[str] = Field(default_factory=list)
    is_universal: bool = False
    studio_ids: List[str] = Field(default_factory=list)
    industries: List[str] = Field(default_factory=list)
    entity_attributes_specs: Dict[str, EntityAttributeSpec] = Field(default_factory=dict)
    required_images: Dict[str, ImageQueryHint] = Field(default_factory=dict)
    created_by: str


class BrandRegistryInputForCreate(BaseModel):
    """
    Partial brand registry for create.
    """
    name: str
    description: str
    tags: List[str] = []
    account_ids: List[str] = []
    studio_ids: List[str] = []
    is_universal: bool = False
    industries: List[str] = []
    entity_attributes_specs: Dict[str, EntityAttributeSpec] = Field(default_factory=dict)
    required_images: Dict[str, ImageQueryHint] = Field(default_factory=dict)
    created_by: str


class Brand(BaseModel):
    """
    Brand - Runtime data interface.
    """
    # BASE LAYER
    id: Optional[str] = None  # Optional: frontend uses 'id', backend uses '_id' from Mongoose
    name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str

    # CORE BRAND LAYER
    logos: List[Logo] = Field(default_factory=list)  # brand logos (with new logo extended type)
    color_palletes: Dict[str, ColorPalette] = Field(default_factory=dict)  # brand color palettes
    brand_rules: List[BrandRule] = Field(default_factory=list)

    # META LAYER
    is_univseral: bool = False
    entity_attributes: Dict[str, Any] = Field(default_factory=dict)  # entity attributes for the brand (e.g. industry, team name, etc.)
    brand_registry_id: str

    # CA / FLOW DATA LAYER
    account_ids: List[str] = Field(default_factory=list)
    studio_ids: List[str] = Field(default_factory=list)
    images: Dict[str, Dict[str, Any]] = Field(default_factory=dict)  # images for the brand (team star, team players) -> configured in the brand registry
    batch_ids: List[str] = Field(default_factory=list)  # batch ids for the brand (used to associate with batch images)

    # Parent / Child Relationships
    parent_brand_ids: List[str] = Field(default_factory=list)  # parent brand ids for the brand
    child_brand_ids: List[str] = Field(default_factory=list)  # child brand ids for the brand


class BrandWithoutId(BaseModel):
    """
    Brand for insert.
    """
    name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    logos: List[Logo] = Field(default_factory=list)
    color_palletes: Dict[str, ColorPalette] = Field(default_factory=dict)
    brand_rules: List[BrandRule] = Field(default_factory=list)
    is_univseral: bool = False
    entity_attributes: Dict[str, Any] = Field(default_factory=dict)
    brand_registry_id: str
    account_ids: List[str] = Field(default_factory=list)
    studio_ids: List[str] = Field(default_factory=list)
    images: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    batch_ids: List[str] = Field(default_factory=list)
    parent_brand_ids: List[str] = Field(default_factory=list)
    child_brand_ids: List[str] = Field(default_factory=list)


class BrandInputForCreate(BaseModel):
    """
    Partial brand for create.
    """
    name: str
    description: str
    created_by: str
    brand_registry_id: str
    tags: List[str] = Field(default_factory=list)
    logos: List[Logo] = Field(default_factory=list)
    color_palletes: Dict[str, ColorPalette] = Field(default_factory=dict)
    brand_rules: List[BrandRule] = Field(default_factory=list)
    is_univseral: bool = False
    entity_attributes: Dict[str, Any] = Field(default_factory=dict)
    account_ids: List[str] = Field(default_factory=list)
    studio_ids: List[str] = Field(default_factory=list)
    images: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    batch_ids: List[str] = Field(default_factory=list)
    parent_brand_ids: List[str] = Field(default_factory=list)
    child_brand_ids: List[str] = Field(default_factory=list)


class BrandInputWithoutId(BaseModel):
    """
    Brand for update (without id).
    """
    name: str
    description: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str
    tags: List[str] = Field(default_factory=list)
    logos: List[Logo] = Field(default_factory=list)
    color_palletes: Dict[str, ColorPalette] = Field(default_factory=dict)
    brand_rules: List[BrandRule] = Field(default_factory=list)
    is_univseral: bool = False
    entity_attributes: Dict[str, Any] = Field(default_factory=dict)
    brand_registry_id: str
    account_ids: List[str] = Field(default_factory=list)
    studio_ids: List[str] = Field(default_factory=list)
    images: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    batch_ids: List[str] = Field(default_factory=list)
    parent_brand_ids: List[str] = Field(default_factory=list)
    child_brand_ids: List[str] = Field(default_factory=list)
