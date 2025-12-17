"""
ODS Types - Enums
Core enumerations for the ODS (Optikka Design System).
Contains both renderer enums and data layer enums used across microservices.
"""

from enum import Enum


# =============================================================================
# RENDERER ENUMS - Used by the frontend/renderer
# =============================================================================

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


# =============================================================================
# DATA LAYER ENUMS - Used by backend microservices
# =============================================================================

class HTTPMethod(str, Enum):
    """HTTP method"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class ImageMimeType(str, Enum):
    """Image MIME types supported by ODS"""
    JPEG = "image/jpeg"
    PNG = "image/png"
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


class TextType(str, Enum):
    """Text input type for template specs"""
    SELECT = "select"
    NUMBER = "number"
    STRING = "string"


class CanvasGuideKind(str, Enum):
    """Canvas guide kind"""
    BOX = "box"
    POINT = "point"


class CanvasGridKind(str, Enum):
    """Canvas grid type"""
    SIMPLE = "simple"
    BENTO = "bento"


class BentoAxis(str, Enum):
    """Bento grid axis"""
    ROW = "row"
    COL = "col"


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


class TargetInputJobStatus(str, Enum):
    """Target input job status"""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"


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
    """Data type for entity attributes"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    ENUM = "enum"
