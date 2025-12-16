"""
ODS Models - Base Types
Base enums and types used across ODS models.
Python equivalent of @optikka/ods-models/base
"""

from enum import Enum


class ImageMimeType(str, Enum):
    """
    Image MIME types supported by ODS.
    Matches design-data-microservices Python models.
    """
    PNG = "image/png"
    JPEG = "image/jpeg"
    GIF = "image/gif"
    WEBP = "image/webp"
    SVG = "image/svg+xml"


class ReviewStatusEnum(str, Enum):
    """Review status for workflow execution results"""
    APPROVED = "APPROVED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"


class ImageTypeEnum(str, Enum):
    """Image type classification"""
    ORIGINAL = "ORIGINAL"
    WORK_IN_PROGRESS = "WORK_IN_PROGRESS"
    LEAF = "LEAF"
    DEBUG = "DEBUG"


class BatchTypeEnum(str, Enum):
    """Workflow batch type"""
    UPLOAD = "UPLOAD"
    DOWNLOAD = "DOWNLOAD"
    SHARED = "SHARED"
    WORKFLOW_RUN = "WORKFLOW_RUN"


class BatchStatusEnum(str, Enum):
    """Workflow batch status"""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExecutionStatusEnum(str, Enum):
    """Kore execution status"""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DesignDataInputTypes(str, Enum):
    """Design data input types"""
    ASSETS = "assets"
    LOGOS = "logos"
    TEXTS = "texts"
    EXTRA_DATA = "extra_data"


class HTTPMethod(str, Enum):
    """HTTP method"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
