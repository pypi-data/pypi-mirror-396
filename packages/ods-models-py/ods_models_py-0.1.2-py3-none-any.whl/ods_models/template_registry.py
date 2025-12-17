"""
ODS Models - Template Registry
Template metadata and configuration.
Python equivalent of template registry from design-data-microservices.
"""

from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from ods_models.input_parameters import (
    InputParameters,
    InputParametersPartialForCreate,
    AssetSpecs,
    TextSpecs,
    LogoSpecs,
)
from ods_models.canvas_globals import CanvasGlobals, FlexPreset


class TemplateRegistry(BaseModel):
    """
    Main template registry entity.
    Runtime data interface for template metadata and configuration.
    """
    id: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = []
    input_parameters: InputParameters
    account_ids: List[str] = Field(default_factory=list)
    studio_ids: List[str] = Field(default_factory=list)
    asset_count: int = 0
    texts_count: int = 0
    logos_count: int = 0
    uses_extra_data: bool = False
    description: str
    created_by: str
    ods_script_s3_location: Dict[str, Any] = {}
    canvas_globals: CanvasGlobals


class TemplateRegistryWithoutId(BaseModel):
    """Template registry for insert operations (no id field)"""
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = []
    input_parameters: InputParameters
    account_ids: List[str] = Field(default_factory=list)
    studio_ids: List[str] = Field(default_factory=list)
    asset_count: int = 0
    texts_count: int = 0
    logos_count: int = 0
    uses_extra_data: bool = False
    description: str
    ods_script_s3_location: Dict[str, Any] = {}
    created_by: str
    canvas_globals: CanvasGlobals


class TemplateRegistryInputForCreate(BaseModel):
    """Partial template registry for create operations"""
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = []
    input_parameters: InputParametersPartialForCreate
    account_ids: List[str] = []
    studio_ids: List[str] = []
    uses_extra_data: bool = False
    description: str
    created_by: str


class ODSScript(BaseModel):
    """ODS script entity"""
    id: str
    s3Location: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    template_registry_ids: List[str] = Field(default_factory=list)


class TemplateRecipe(BaseModel):
    """
    A template recipe is an ODS script + template registry.
    Wrapper model combining script and registry.
    """
    ods_script: ODSScript
    template_registry: TemplateRegistry


# ============================================================================
# API Body Models for Template Registry Operations
# ============================================================================

class AddAssetToTemplateRegistryBody(BaseModel):
    """Add asset to template registry body"""
    asset_spec: AssetSpecs


class AddTextToTemplateRegistryBody(BaseModel):
    """Add text to template registry body"""
    text_spec: TextSpecs


class AddLogoToTemplateRegistryBody(BaseModel):
    """Add logo to template registry body"""
    logo_spec: LogoSpecs


class AddExtraDataToTemplateRegistryBody(BaseModel):
    """Add extra data to template registry body"""
    extra_data: Dict[str, Any]


class RemoveExtraDataFromTemplateRegistryBody(BaseModel):
    """Remove extra data from template registry body"""
    extra_data_keys: List[str]


class AddFlexPresetToTemplateRegistryBody(BaseModel):
    """Add flex preset to template registry body"""
    flex_preset: FlexPreset


class UpdateStudioAndAccountIdsForTemplateRegistryBody(BaseModel):
    """Update studio and account ids for template registry body"""
    studio_ids: List[str]
    account_ids: List[str]
