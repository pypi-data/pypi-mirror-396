"""
ODS Types - Common Types
Common type definitions for the ODS (Optikka Design System) renderer.
Python equivalent of @optikka/ods-types/common
"""

from typing import TypedDict, Optional
from ods_types.enums import TargetKind


class Target(TypedDict, total=False):
    """
    Target reference for design elements.
    Specifies what element a verb or action should target.
    """
    kind: TargetKind
    id: Optional[str]
    layerId: Optional[str]


class Box(TypedDict):
    """
    Box represents a rectangular region with position and dimensions.
    Used throughout the rendering system for positioning and sizing.
    """
    x: float
    y: float
    w: float
    h: float


class DrawImageParams(TypedDict):
    """
    Parameters for ctx.drawImage() - used for rendering images with different objectFit modes.
    Maps to HTML Canvas API drawImage() method parameters.
    """
    sx: float       # Source X (crop start)
    sy: float       # Source Y (crop start)
    sWidth: float   # Source width (crop width)
    sHeight: float  # Source height (crop height)
    dx: float       # Destination X
    dy: float       # Destination Y
    dWidth: float   # Destination width
    dHeight: float  # Destination height
