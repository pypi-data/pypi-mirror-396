"""
ODS Types - Python Implementation
Core types and enums for the ODS (Optikka Design System).
Python equivalent of @optikka/ods-types npm package.
"""

__version__ = "0.1.1"

# Re-export all enums
from ods_types.enums import (
    # Renderer enums
    Kind,
    TargetKind,
    FadeKind,
    Easing,
    Dimension,
    AlignX,
    AlignY,
    LayerKind,
    TextKind,
    FillKind,
    DropZoneMode,
    SlideKind,
    StackDir,
    StackAlign,
    ClampAxes,
    AspectMode,
    ScaleMode,
    # Data layer enums
    HTTPMethod,
    ImageMimeType,
    ReviewStatusEnum,
    ImageTypeEnum,
    BatchTypeEnum,
    BatchStatusEnum,
    ExecutionStatusEnum,
    DesignDataInputTypes,
    TextType,
    CanvasGuideKind,
    CanvasGridKind,
    BentoAxis,
    RenderRunStatus,
    RenderRunQueueEventType,
    TargetInputJobStatus,
    ColorType,
    BrandRuleType,
    BrandRuleTarget,
    DataType,
)

# Re-export all common types
from ods_types.common import (
    Target,
    Box,
    DrawImageParams,
)

__all__ = [
    # Renderer enums
    "Kind",
    "TargetKind",
    "FadeKind",
    "Easing",
    "Dimension",
    "AlignX",
    "AlignY",
    "LayerKind",
    "TextKind",
    "FillKind",
    "DropZoneMode",
    "SlideKind",
    "StackDir",
    "StackAlign",
    "ClampAxes",
    "AspectMode",
    "ScaleMode",
    # Data layer enums
    "HTTPMethod",
    "ImageMimeType",
    "ReviewStatusEnum",
    "ImageTypeEnum",
    "BatchTypeEnum",
    "BatchStatusEnum",
    "ExecutionStatusEnum",
    "DesignDataInputTypes",
    "TextType",
    "CanvasGuideKind",
    "CanvasGridKind",
    "BentoAxis",
    "RenderRunStatus",
    "RenderRunQueueEventType",
    "TargetInputJobStatus",
    "ColorType",
    "BrandRuleType",
    "BrandRuleTarget",
    "DataType",
    # Common types
    "Target",
    "Box",
    "DrawImageParams",
]
