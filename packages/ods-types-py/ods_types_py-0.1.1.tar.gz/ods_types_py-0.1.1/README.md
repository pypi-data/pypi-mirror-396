# ods-types-py

Core types and enums for the ODS (Optikka Design System) renderer - Python implementation.

This is the Python equivalent of the `@optikka/ods-types` npm package, providing shared type definitions and enumerations used across ODS rendering services.

## Installation

```bash
pip install ods-types-py
```

## Usage

```python
from ods_types import (
    Kind,
    TargetKind,
    AspectMode,
    ScaleMode,
    Box,
    Target,
)

# Use enums
kind = Kind.CANVAS
aspect = AspectMode.CONTAIN

# Use type definitions
box: Box = {"x": 0, "y": 0, "w": 100, "h": 100}
target: Target = {"kind": TargetKind.LAYER, "id": "layer-1"}
```

## Package Contents

### Enums
- `Kind` - Canvas or layer types
- `TargetKind` - Target reference types (canvas, layer, guide, self)
- `AspectMode` - Aspect ratio modes (contain, cover, fitWidth, fitHeight)
- `ScaleMode` - Scaling modes for images and layers
- `AlignX`, `AlignY` - Alignment options
- `DropZoneMode` - Drop zone fit modes
- `StackDir`, `StackAlign` - Stack layout options
- `FadeKind`, `SlideKind` - Animation types
- `Easing` - Animation easing functions
- And more...

### Common Types
- `Box` - Rectangular region with x, y, w, h
- `Target` - Target reference with kind, id, and layerId
- `DrawImageParams` - Canvas drawImage parameters

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/

# Lint
ruff check src/ tests/
```

## License

PROPRIETARY - Optikka
