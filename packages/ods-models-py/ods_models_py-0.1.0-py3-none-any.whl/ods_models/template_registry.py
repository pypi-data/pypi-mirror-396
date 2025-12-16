"""
ODS Models - Template Registry
Template metadata and configuration.
Python equivalent of @optikka/ods-models/templateRegistry
"""

from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from ods_models.input_parameters import InputParameters, InputParametersPartialForCreate
from ods_models.canvas_globals import CanvasGlobals


class TemplateRegistry(BaseModel):
    """
    Main template registry entity.
    Runtime data interface for template metadata and configuration.
    Matches design-data-microservices Python models (source of truth).
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
