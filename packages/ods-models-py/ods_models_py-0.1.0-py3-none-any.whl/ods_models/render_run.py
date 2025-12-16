"""
ODS Models - Render Run
Render run models for batch rendering operations.
Python equivalent of @optikka/ods-models/renderRun
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class RenderRunStatus(str, Enum):
    """Render run status"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RenderRunQueueEventType(str, Enum):
    """Render run event type"""
    RENDER = "render"
    FINISH_RENDER_RUN = "finish_render_run"


class RenderRun(BaseModel):
    """Render run entity for batch rendering operations"""
    id: str
    template_registry_id: str
    csv_s3_location: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: str
    account_id: str
    studio_id: str
    batch_name: str
    status: RenderRunStatus


class RenderRunInputForCreate(BaseModel):
    """Render run input for create operations"""
    template_registry_id: str
    created_by: str
    account_id: str
    studio_id: str
    tags: Optional[List[str]] = Field(default_factory=list)
    batch_name: str
    file_name: str


class RenderRunWithoutId(BaseModel):
    """Render run for insert operations (no id field)"""
    template_registry_id: str
    csv_s3_location: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: str
    account_id: str
    studio_id: str
    batch_name: str
    status: RenderRunStatus


class StartRenderRunFromTargetInputJobInput(BaseModel):
    """Create render run from target input job input"""
    template_input_job_id: str


class TargetInputJobImage(BaseModel):
    """Image in target input job"""
    filename: str
    parsing_label: str
    s3_location: Dict[str, Any]
    width: int
    height: int
    mime_type: str
    original_image_id: Optional[str] = None
    image_id: Optional[str] = None
    guides: Optional[List[Dict[str, Any]]] = []
    workflow_registry_ids: Optional[str] = None
    wer_ids: Optional[str] = None


class Progress(BaseModel):
    """Progress tracking for jobs"""
    total_batches: int
    completed_batches: int
    failed_batches: int


class Mapping(BaseModel):
    """CSV column to template field mapping"""
    csv_column: str
    template_field: str
    field_type: str
    confidence: float


class TargetInputJobResult(BaseModel):
    """Result of target input job processing"""
    csv_rows: List[Dict[str, Any]] = []
    mappings: List[Mapping] = []
    csv_s3_location: Optional[Dict[str, Any]] = None


class TargetInputJobStatus(str, Enum):
    """Target input job status"""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"


class TargetInputJob(BaseModel):
    """Target input job for processing template inputs"""
    job_id: str
    status: TargetInputJobStatus
    template_registry_id: str
    render_target_group_prefix: str
    progress: Progress
    created_at: datetime
    updated_at: datetime
    expires_at: int
    render_run_id: str
    csv_s3_location: Optional[Dict[str, Any]] = None
    images: List[Dict[str, Any]] = []
    csv_description: Optional[str] = None
    result: Optional[TargetInputJobResult] = None
