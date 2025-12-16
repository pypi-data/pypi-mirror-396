"""
ODS Types - Python Implementation
Core types and enums for the ODS (Optikka Design System) renderer.
Python equivalent of @optikka/ods-types npm package.
"""

__version__ = "0.1.0"

# Re-export all enums
from ods_types.enums import (
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
    # Enums
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
    "ColorType",
    "BrandRuleType",
    "BrandRuleTarget",
    "DataType",
    # Common types
    "Target",
    "Box",
    "DrawImageParams",
]
