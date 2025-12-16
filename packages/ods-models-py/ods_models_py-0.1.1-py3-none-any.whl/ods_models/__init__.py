"""
ODS Models - Python Implementation
Pydantic data models for the ODS (Optikka Design System).
Python equivalent of @optikka/ods-models npm package.
"""

__version__ = "0.1.0"

# Re-export base enums
from ods_models.base import (
    ImageMimeType,
    ReviewStatusEnum,
    ImageTypeEnum,
    BatchTypeEnum,
    BatchStatusEnum,
    ExecutionStatusEnum,
    DesignDataInputTypes,
    HTTPMethod,
)

# Re-export guides
from ods_models.guides import GuideDoc

# Re-export canvas globals
from ods_models.canvas_globals import (
    CanvasGuideKind,
    CanvasGridKind,
    BentoAxis,
    FlexPreset,
    CanvasGuides,
    CanvasGridBase,
    CanvasSimpleGridDef,
    CanvasBentoGridDef,
    CanvasBentoNode,
    CanvasGridDef,
    CanvasGlobals,
)

# Re-export input parameters
from ods_models.input_parameters import (
    TextTypeEnum,
    AssetSpecs,
    LogoSpecs,
    TextSpecs,
    InputParameters,
    InputParametersPartialForCreate,
)

# Re-export template input
from ods_models.template_input import (
    Asset,
    Logo,
    Text,
    TemplateInputDesignData,
    TemplateInput,
    TemplateInputWithoutId,
    TemplateInputForCreate,
)

# Re-export template registry
from ods_models.template_registry import (
    TemplateRegistry,
    TemplateRegistryWithoutId,
    TemplateRegistryInputForCreate,
    ODSScript,
    TemplateRecipe,
    # API body models
    AddAssetToTemplateRegistryBody,
    AddTextToTemplateRegistryBody,
    AddLogoToTemplateRegistryBody,
    AddExtraDataToTemplateRegistryBody,
    RemoveExtraDataFromTemplateRegistryBody,
    AddFlexPresetToTemplateRegistryBody,
    UpdateStudioAndAccountIdsForTemplateRegistryBody,
)

# Re-export render run
from ods_models.render_run import (
    RenderRunStatus,
    RenderRunQueueEventType,
    RenderRun,
    RenderRunInputForCreate,
    RenderRunWithoutId,
    StartRenderRunFromTargetInputJobInput,
    TargetInputJobImage,
    Progress,
    Mapping,
    TargetInputJobResult,
    TargetInputJobStatus,
    TargetInputJob,
)

# Re-export image and workflow models
from ods_models.image import (
    Image,
    WorkflowExecutionResult,
    WorkflowBatch,
    KoreExecution,
    ResizeParams,
)

# Re-export brand models
from ods_models.brand import (
    RGB,
    HSL,
    HSV,
    CMYK,
    Color,
    ColorPalette,
    BrandRule,
    ImageQueryHint,
    EntityAttributeSpec,
    BrandRegistry,
    BrandRegistryWithoutId,
    BrandRegistryInputForCreate,
    Brand,
    BrandWithoutId,
    BrandInputForCreate,
    BrandInputWithoutId,
)

__all__ = [
    # Base enums
    "ImageMimeType",
    "ReviewStatusEnum",
    "ImageTypeEnum",
    "BatchTypeEnum",
    "BatchStatusEnum",
    "ExecutionStatusEnum",
    "DesignDataInputTypes",
    "HTTPMethod",
    # Guides
    "GuideDoc",
    # Canvas globals
    "CanvasGuideKind",
    "CanvasGridKind",
    "BentoAxis",
    "FlexPreset",
    "CanvasGuides",
    "CanvasGridBase",
    "CanvasSimpleGridDef",
    "CanvasBentoGridDef",
    "CanvasBentoNode",
    "CanvasGridDef",
    "CanvasGlobals",
    # Input parameters
    "TextTypeEnum",
    "AssetSpecs",
    "LogoSpecs",
    "TextSpecs",
    "InputParameters",
    "InputParametersPartialForCreate",
    # Template input
    "Asset",
    "Logo",
    "Text",
    "TemplateInputDesignData",
    "TemplateInput",
    "TemplateInputWithoutId",
    "TemplateInputForCreate",
    # Template registry
    "TemplateRegistry",
    "TemplateRegistryWithoutId",
    "TemplateRegistryInputForCreate",
    "ODSScript",
    "TemplateRecipe",
    # Template registry API body models
    "AddAssetToTemplateRegistryBody",
    "AddTextToTemplateRegistryBody",
    "AddLogoToTemplateRegistryBody",
    "AddExtraDataToTemplateRegistryBody",
    "RemoveExtraDataFromTemplateRegistryBody",
    "AddFlexPresetToTemplateRegistryBody",
    "UpdateStudioAndAccountIdsForTemplateRegistryBody",
    # Render run
    "RenderRunStatus",
    "RenderRunQueueEventType",
    "RenderRun",
    "RenderRunInputForCreate",
    "RenderRunWithoutId",
    "StartRenderRunFromTargetInputJobInput",
    "TargetInputJobImage",
    "Progress",
    "Mapping",
    "TargetInputJobResult",
    "TargetInputJobStatus",
    "TargetInputJob",
    # Image and workflow
    "Image",
    "WorkflowExecutionResult",
    "WorkflowBatch",
    "KoreExecution",
    "ResizeParams",
    # Brand models
    "RGB",
    "HSL",
    "HSV",
    "CMYK",
    "Color",
    "ColorPalette",
    "BrandRule",
    "ImageQueryHint",
    "EntityAttributeSpec",
    "BrandRegistry",
    "BrandRegistryWithoutId",
    "BrandRegistryInputForCreate",
    "Brand",
    "BrandWithoutId",
    "BrandInputForCreate",
    "BrandInputWithoutId",
]
