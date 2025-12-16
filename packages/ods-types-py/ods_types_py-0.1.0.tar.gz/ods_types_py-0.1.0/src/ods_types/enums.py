"""
ODS Types - Enums
Core enumerations for the ODS (Optikka Design System) renderer.
Python equivalent of @optikka/ods-types/enums
"""

from enum import Enum


class Kind(str, Enum):
    """Kind of design element"""
    CANVAS = "canvas"
    LAYER = "layer"


class TargetKind(str, Enum):
    """Target reference types"""
    CANVAS = "canvas"
    LAYER = "layer"
    GUIDE = "guide"
    SELF = "self"


class FadeKind(str, Enum):
    """Fade animation types"""
    PHASE = "phase"


class Easing(str, Enum):
    """Animation easing functions"""
    EASE_IN = "easeIn"
    EASE_OUT = "easeOut"
    EASE_IN_OUT = "easeInOut"
    LINEAR = "linear"


class Dimension(str, Enum):
    """Dimension types"""
    WIDTH = "width"
    HEIGHT = "height"


class AlignX(str, Enum):
    """Horizontal alignment options"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    MIDDLE = "middle"


class AlignY(str, Enum):
    """Vertical alignment options"""
    TOP = "top"
    CENTER = "center"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class LayerKind(str, Enum):
    """Layer reference types"""
    SELF = "self"
    OTHER = "other"  # other layer by id


class TextKind(str, Enum):
    """Text visibility types"""
    PUBLIC = "public"
    PRIVATE = "private"


class FillKind(str, Enum):
    """Fill visibility types"""
    PUBLIC = "public"
    PRIVATE = "private"


class DropZoneMode(str, Enum):
    """Drop zone fit modes"""
    CONTAIN = "contain"
    COVER = "cover"
    FIT_WIDTH = "fitWidth"
    FIT_HEIGHT = "fitHeight"


class SlideKind(str, Enum):
    """Slide animation types"""
    CANVAS = "canvas"
    LAYER = "layer"
    PHASE = "phase"


class StackDir(str, Enum):
    """Stack direction"""
    RIGHT = "right"
    LEFT = "left"
    UP = "up"
    DOWN = "down"


class StackAlign(str, Enum):
    """Stack alignment"""
    START = "start"
    CENTER = "center"
    END = "end"


class ClampAxes(str, Enum):
    """Clamp axes options"""
    X = "x"
    Y = "y"
    BOTH = "both"


class AspectMode(str, Enum):
    """Aspect ratio modes"""
    CONTAIN = "contain"
    COVER = "cover"
    FIT_WIDTH = "fitWidth"
    FIT_HEIGHT = "fitHeight"


class ScaleMode(str, Enum):
    """Scaling modes for images and layers"""
    WIDTH = "width"
    HEIGHT = "height"
    MIN_SIDE = "minSide"
    MAX_SIDE = "maxSide"
    HEIGHT_FROM_WIDTH = "heightFromWidth"
    WIDTH_FROM_HEIGHT = "widthFromHeight"
    WIDTH_FROM_MIN_SIDE = "widthFromMinSide"
    WIDTH_FROM_MAX_SIDE = "widthFromMaxSide"
    HEIGHT_FROM_MIN_SIDE = "heightFromMinSide"
    HEIGHT_FROM_MAX_SIDE = "heightFromMaxSide"


class ColorType(str, Enum):
    """Color type classification"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    ACCENT = "accent"
    NEUTRAL = "neutral"
    BACKGROUND = "background"


class BrandRuleType(str, Enum):
    """Brand rule type"""
    COLOR = "color"
    LOGO = "logo"
    FONT = "font"
    TYPOGRAPHY = "typography"
    VISUAL_IDENTITY = "visual_identity"


class BrandRuleTarget(str, Enum):
    """Brand rule target"""
    LOGO = "logo"
    COLOR = "color"
    FONT = "font"
    TYPOGRAPHY = "typography"
    VISUAL_IDENTITY = "visual_identity"


class DataType(str, Enum):
    """Data type"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    ENUM = "enum"
